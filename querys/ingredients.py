import duckdb

con = duckdb.connect("sales.duckdb", read_only=True)

ingredient = 'Pearl'
date_start = '2026-09-14'
date_end = '2026-09-27'

# Modifier name, recipe ingredient name, standalone topping menu name
aliases = {
    "Pearl": ("Pearl", "Pearls", "Pearls")
}

modifier, recipe_name, topping_name = aliases.get(
    ingredient, (ingredient, ingredient, ingredient)
)

sql = """
WITH params AS (
    SELECT
        ? AS modifier_name,
        ? AS recipe_name,
        ? AS topping_name,
        CAST(? AS DATE) AS date_start,
        CAST(? AS DATE) AS date_end
),
sales_data AS MATERIALIZED (
    SELECT
        ROW_NUMBER() OVER () AS sale_id,
        UPPER(TRIM(CAST(s."SKU" AS VARCHAR))) AS sku,
        TRY_CAST(s."Qty" AS DOUBLE) AS qty,
        COALESCE(s."modifiers_applied", '') AS modifiers
    FROM sales s
    CROSS JOIN params p
    WHERE CAST(s."Date" AS DATE)
          BETWEEN p.date_start AND p.date_end
),
ingredient_recipes AS (
    SELECT
        UPPER(TRIM(CAST(r.sku AS VARCHAR))) AS sku,
        TRY_CAST(r.quantity AS DOUBLE) AS quantity
    FROM recipes r
    CROSS JOIN params p
    WHERE LOWER(TRIM(r.ingredient_name)) = LOWER(p.recipe_name)
),
topping_unit AS (
    SELECT COALESCE(MAX(TRY_CAST(r.quantity AS DOUBLE)), 0) AS quantity
    FROM recipes r
    CROSS JOIN params p
    WHERE LOWER(TRIM(r.menu_name)) = LOWER(p.topping_name)
      AND LOWER(TRIM(r.ingredient_name)) = LOWER(p.recipe_name)
),
modifier_extras AS (
    SELECT
        s.sale_id,
        SUM(
            COALESCE(
                TRY_CAST(
                    REGEXP_EXTRACT(
                        TRIM(u.modifier),
                        '[×xX*][[:space:]]*([0-9]+([.][0-9]+)?)[[:space:]]*$',
                        1
                    ) AS DOUBLE
                ),
                1
            )
        ) AS extra_qty
    FROM sales_data s
    CROSS JOIN UNNEST(STRING_SPLIT(s.modifiers, ',')) AS u(modifier)
    CROSS JOIN params p
    WHERE LOWER(TRIM(REGEXP_REPLACE(
        TRIM(u.modifier),
        '[[:space:]]*[×xX*][[:space:]]*[0-9]+([.][0-9]+)?[[:space:]]*$',
        ''
    ))) = LOWER(p.modifier_name)
    GROUP BY s.sale_id
),
base_consumption AS (
    SELECT COALESCE(SUM(s.qty * r.quantity), 0) AS amount
    FROM sales_data s
    JOIN ingredient_recipes r ON s.sku = r.sku
),
extra_consumption AS (
    SELECT COALESCE(
        SUM(s.qty * COALESCE(r.quantity, t.quantity) * m.extra_qty),
        0
    ) AS amount
    FROM sales_data s
    JOIN modifier_extras m ON s.sale_id = m.sale_id
    LEFT JOIN ingredient_recipes r ON s.sku = r.sku
    CROSS JOIN topping_unit t
)
SELECT
    b.amount AS base_consumption,
    e.amount AS extra_consumption,
    b.amount + e.amount AS total_consumption
FROM base_consumption b
CROSS JOIN extra_consumption e;
"""

result = con.execute(
    sql,
    [modifier, recipe_name, topping_name, date_start, date_end]
).fetchdf()

print(result)


con.close()