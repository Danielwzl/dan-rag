import duckdb
import pandas as pd

con = duckdb.connect("sales.duckdb", read_only=True)

ingredient = 'Strawberry Jam'
date_start = '2026-09-14'
date_end = '2026-10-18'

sql = """
WITH params AS (
    SELECT
        CAST(? AS DATE) AS date_start,
        CAST(? AS DATE) AS date_end,
        ? AS topping_name,
),
sales_data AS MATERIALIZED (
    SELECT
        location,
        item,
        ROW_NUMBER() OVER () AS sale_id,
        UPPER(TRIM(CAST("SKU" AS VARCHAR))) AS sku,
        ABS(TRY_CAST("Qty" AS DOUBLE)) AS qty,
COALESCE("modifiers_applied", '') AS modifiers
    FROM sales
    CROSS JOIN params p
    WHERE CAST("Date" AS DATE)
          BETWEEN p.date_start AND p.date_end
),

usage_per_cup AS (
    SELECT
        r.menu_name as item_name,
        UPPER(TRIM(CAST(r.sku AS VARCHAR))) AS sku,
        TRY_CAST(r.quantity AS DOUBLE) AS quantity
    FROM recipes_strawb_921 r
    CROSS JOIN params p
    WHERE LOWER(TRIM(r.ingredient_name)) = LOWER(topping_name)
),

topping_unit AS (
    SELECT COALESCE(MAX(TRY_CAST(quantity AS DOUBLE)), 0) AS quantity
    FROM recipes_strawb_921
    CROSS JOIN params p
    WHERE LOWER(TRIM(menu_name)) = LOWER(p.topping_name)
),

base_consumption AS (
    SELECT SUM(s.qty * u.quantity) as quantity, s.location
    FROM sales_data s
    JOIN usage_per_cup u ON s.sku = u.sku
    GROUP BY s.location
),

modifier_extras AS (
    SELECT
        s.sale_id,
        SUM(
            COALESCE(
                TRY_CAST(
                    REGEXP_EXTRACT(
                        TRIM(m.modifier),
                        '[×xX*][[:space:]]*([0-9]+([.][0-9]+)?)[[:space:]]*$',
                        1
                    ) AS DOUBLE
                ),
                1.0
            )
        ) AS extra_qty
    FROM sales_data s
    CROSS JOIN params p
    CROSS JOIN UNNEST(
        STRING_SPLIT(s.modifiers, ',')
    ) AS m(modifier)
    WHERE LOWER(TRIM(
        REGEXP_REPLACE(
            TRIM(m.modifier),
            '[[:space:]]*[×xX*][[:space:]]*[0-9]+([.][0-9]+)?[[:space:]]*$',
            ''
        )
    )) IN (LOWER(p.topping_name), LOWER(p.topping_name))
    GROUP BY s.sale_id
    ORDER BY s.sale_id
),

extra_consumption AS (
    SELECT COALESCE(
        SUM(
            s.qty * p.quantity * m.extra_qty
        ),
        0
    ) AS quantity, s.location
    FROM sales_data s
    JOIN modifier_extras m ON s.sale_id = m.sale_id
    CROSS JOIN topping_unit p
    GROUP BY s.location
),

locations AS (
    SELECT DISTINCT location
    FROM sales_data
),

result_data AS (
    SELECT
        l.location,
        b.quantity AS base_consumption,
        e.quantity AS extra_consumption,
        b.quantity + e.quantity AS total_consumption
    FROM locations l
    LEFT JOIN base_consumption b ON l.location = b.location
    LEFT JOIN extra_consumption e ON l.location = e.location
    ORDER BY l.location
)

SELECT *
FROM (
    SELECT
        location,
        base_consumption,
        extra_consumption,
        total_consumption
    FROM result_data

    UNION ALL

    SELECT
        'TOTAL' AS location,
        SUM(base_consumption),
        SUM(extra_consumption),
        SUM(total_consumption)
    FROM result_data
) final_result
ORDER BY
    CASE WHEN location = 'TOTAL' THEN 1 ELSE 0 END,
    location;
"""

result = con.execute(
    sql,
    [date_start, date_end, ingredient]
).fetchdf()
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(result)
print(f'{ingredient}: {date_start} - {date_end}')

con.close()