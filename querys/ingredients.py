import duckdb
import pandas as pd

con = duckdb.connect("sales.duckdb", read_only=True)

ingredient = 'Pearl'
date_start = '2026-09-14'
date_end = '2026-09-27'

modifier, recipe_name, topping_name = (ingredient, ingredient, ingredient)

# sql = """
# WITH sales_data AS MATERIALIZED (
#     SELECT
#         ROW_NUMBER() OVER () AS sale_id,
#         UPPER(TRIM(CAST("SKU" AS VARCHAR))) AS sku,
#         ABS(TRY_CAST("Qty" AS DOUBLE)) AS qty,
#         COALESCE("modifiers_applied", '') AS modifiers
#     FROM sales
#     WHERE CAST("Date" AS DATE)
#           BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
# ),

# ingredient_recipes AS (
#     SELECT
#         UPPER(TRIM(CAST(r.sku AS VARCHAR))) AS sku,
#         SUM(TRY_CAST(r.quantity AS DOUBLE)) AS quantity
#     FROM recipes r
#     WHERE LOWER(TRIM(r.ingredient_name)) = LOWER(?)
#     GROUP BY r.sku
# ),

# topping_unit AS (
#     SELECT COALESCE(MAX(TRY_CAST(quantity AS DOUBLE)), 0) AS quantity
#     FROM recipes
#     WHERE LOWER(TRIM(menu_name)) = LOWER(?)
#       AND LOWER(TRIM(ingredient_name)) = LOWER(?)
# ),

# modifier_extras AS (
#     SELECT
#         s.sale_id,
#         SUM(
#             COALESCE(
#                 TRY_CAST(
#                     REGEXP_EXTRACT(
#                         TRIM(m.modifier),
#                         '[×xX*][[:space:]]*([0-9]+([.][0-9]+)?)[[:space:]]*$',
#                         1
#                     ) AS DOUBLE
#                 ),
#                 1.0
#             )
#         ) AS extra_qty
#     FROM sales_data s
#     CROSS JOIN UNNEST(
#         STRING_SPLIT(s.modifiers, ',')
#     ) AS m(modifier)
#     WHERE LOWER(TRIM(
#         REGEXP_REPLACE(
#             TRIM(m.modifier),
#             '[[:space:]]*[×xX*][[:space:]]*[0-9]+([.][0-9]+)?[[:space:]]*$',
#             ''
#         )
#     )) IN (LOWER(?), LOWER(?))
#     GROUP BY s.sale_id
# ),

# base_consumption AS (
#     SELECT COALESCE(SUM(s.qty * r.quantity), 0) AS quantity
#     FROM sales_data s
#     JOIN ingredient_recipes r ON s.sku = r.sku
# ),

# extra_consumption AS (
#     SELECT COALESCE(
#         SUM(
#             s.qty * COALESCE(r.quantity, p.quantity) * m.extra_qty
#         ),
#         0
#     ) AS quantity
#     FROM sales_data s
#     JOIN modifier_extras m ON s.sale_id = m.sale_id
#     LEFT JOIN ingredient_recipes r ON s.sku = r.sku
#     CROSS JOIN topping_unit p
# )

# SELECT
#     b.quantity AS base_consumption,
#     e.quantity AS extra_consumption,
#     b.quantity + e.quantity AS total_consumption
# FROM base_consumption b
# CROSS JOIN extra_consumption e;
# """

sql = """
WITH params AS (
    SELECT
        CAST(? AS DATE) AS date_start,
        CAST(? AS DATE) AS date_end,
        ? AS topping_name,
),
sales_data AS MATERIALIZED (
    SELECT
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
    FROM recipes r
    CROSS JOIN params p
    WHERE LOWER(TRIM(r.ingredient_name)) = LOWER(topping_name)
),

topping_unit AS (
    SELECT COALESCE(MAX(TRY_CAST(quantity AS DOUBLE)), 0) AS quantity
    FROM recipes
    CROSS JOIN params p
    WHERE LOWER(TRIM(menu_name)) = LOWER(p.topping_name)
),

base_consumption AS (
    SELECT SUM(s.qty * u.quantity) as quantity
    FROM sales_data s
    JOIN usage_per_cup u ON s.sku = u.sku
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
    ) AS quantity
    FROM sales_data s
    JOIN modifier_extras m ON s.sale_id = m.sale_id
    CROSS JOIN topping_unit p
)

SELECT
    b.quantity AS base_consumption,
    e.quantity AS extra_consumption,
    b.quantity + e.quantity AS total_consumption
FROM base_consumption b
CROSS JOIN extra_consumption e;
"""

result = con.execute(
    sql,
    [date_start, date_end, ingredient]
).fetchdf()
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(result)


con.close()


# import csv
# import re
# from collections import defaultdict

# # ===== 文件路径 =====
# SALES_FILE = "data/items-2026-09-14-2026-09-27.csv"
# RECIPES_FILE = "data/metadata/recipes.csv"

# # ===== 1. 读取 recipes，建立每个 SKU 的基础 Pearl 消耗 =====
# # 只统计这些 Pearl 类原料：
# # Pearls, White Pearl, Brown Sugar Pearl
# PEARL_INGREDIENTS = {
#     "pearls": 1.0,
#     "white pearl": 1.0,
#     "brown sugar pearl": 1.0,
# }

# # 额外 Pearl 的单位消耗，来自 recipes.csv 里的 modifier 行
# EXTRA_PEARL_UNIT = {
#     "pearl": 0.102,          # TT000001
#     "pearls": 0.102,
#     "white pearl": 0.098,    # TT000005
#     "brown sugar pearl": 0.11,  # TT000013
# }

# base_pearl_by_sku = defaultdict(float)

# with open(RECIPES_FILE, encoding="utf-8-sig") as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         sku = (row.get("sku") or "").strip()
#         ingredient = (row.get("ingredient_name") or "").strip().lower()
#         qty = float(row.get("quantity") or 0)

#         if not sku:
#             continue

#         if ingredient in PEARL_INGREDIENTS:
#             base_pearl_by_sku[sku] += qty

# # ===== 2. 解析 modifiers_applied 中额外 Pearl 数量 =====
# def extra_pearl_from_modifiers(mods):
#     if not mods:
#         return 0.0

#     total = 0.0
#     # 按逗号拆分 modifier
#     parts = re.split(r",", mods)

#     for part in parts:
#         s = part.strip().lower()
#         if not s:
#             continue

#         # 排除 popping pearl
#         if "popping pearl" in s or "popping pearls" in s:
#             continue

#         # 匹配 Pearl / Pearls / White Pearl / Brown Sugar Pearl
#         if "brown sugar pearl" in s:
#             unit = EXTRA_PEARL_UNIT["brown sugar pearl"]
#         elif "white pearl" in s:
#             unit = EXTRA_PEARL_UNIT["white pearl"]
#         elif "pearl" in s:
#             unit = EXTRA_PEARL_UNIT["pearl"]
#         else:
#             continue

#         # 匹配 x2 / × 2.0 / x 3.0
#         m = re.search(r"(?:x|×)\s*([0-9]+(?:\.[0-9]+)?)", s)
#         if m:
#             multiplier = float(m.group(1))
#         else:
#             multiplier = 1.0

#         total += unit * multiplier

#     return total

# # ===== 3. 读取 sales 表并汇总 =====
# total_pearl = 0.0
# base_total = 0.0
# extra_total = 0.0
# detail = defaultdict(float)

# with open(SALES_FILE, encoding="utf-8-sig") as f:
#     reader = csv.DictReader(f)

#     for row in reader:
#         qty = abs(float(row["Qty"]))
#         sku = (row.get("SKU") or "").strip()
#         item = (row.get("Item") or "").strip()
#         mods = row.get("modifiers_applied") or ""

#         base_pearl = base_pearl_by_sku.get(sku, 0.0)
#         extra_pearl = extra_pearl_from_modifiers(mods)

#         pearl_units = qty * (base_pearl + extra_pearl)

#         base_total += qty * base_pearl
#         extra_total += qty * extra_pearl
#         total_pearl += pearl_units

#         detail[(item, sku)] += pearl_units

# # ===== 4. 输出 =====
# print("总 Pearl 消耗 =", round(total_pearl, 6))
# print("其中基础 Pearl =", round(base_total, 6))
# print("其中额外 Pearl =", round(extra_total, 6))
# print("\n按饮品明细（前 50 条）：")
# for (item, sku), units in sorted(detail.items(), key=lambda x: -x[1])[:50]:
#     print(f"{item} | SKU={sku} | Pearl={round(units, 6)}")】


# sql = """
# WITH params AS (
#     SELECT
#         ? AS modifier_name,
#         ? AS recipe_name,
#         ? AS topping_name,
#         CAST(? AS DATE) AS date_start,
#         CAST(? AS DATE) AS date_end
# ),
# sales_data AS MATERIALIZED (
#     SELECT
#         ROW_NUMBER() OVER () AS sale_id,
#         UPPER(TRIM(CAST(s."SKU" AS VARCHAR))) AS sku,
#         ABS(TRY_CAST(s."Qty" AS DOUBLE)) AS qty,
#         COALESCE(s."modifiers_applied", '') AS modifiers
#     FROM sales s
#     CROSS JOIN params p
#     WHERE CAST(s."Date" AS DATE)
#           BETWEEN p.date_start AND p.date_end
# ),
# ingredient_recipes AS (
#     SELECT
#         UPPER(TRIM(CAST(r.sku AS VARCHAR))) AS sku,
#         TRY_CAST(r.quantity AS DOUBLE) AS quantity
#     FROM recipes r
#     CROSS JOIN params p
#     WHERE LOWER(TRIM(r.ingredient_name)) = LOWER(p.recipe_name)
# ),
# topping_unit AS (
#     SELECT COALESCE(MAX(TRY_CAST(r.quantity AS DOUBLE)), 0) AS quantity
#     FROM recipes r
#     CROSS JOIN params p
#     WHERE LOWER(TRIM(r.menu_name)) = LOWER(p.topping_name)
#       AND LOWER(TRIM(r.ingredient_name)) = LOWER(p.recipe_name)
# ),
# modifier_extras AS (
#     SELECT
#         s.sale_id,
#         SUM(
#             COALESCE(
#                 TRY_CAST(
#                     REGEXP_EXTRACT(
#                         TRIM(u.modifier),
#                         '[×xX*][[:space:]]*([0-9]+([.][0-9]+)?)[[:space:]]*$',
#                         1
#                     ) AS DOUBLE
#                 ),
#                 1
#             )
#         ) AS extra_qty
#     FROM sales_data s
#     CROSS JOIN UNNEST(STRING_SPLIT(s.modifiers, ',')) AS u(modifier)
#     CROSS JOIN params p
#     WHERE LOWER(TRIM(REGEXP_REPLACE(
#         TRIM(u.modifier),
#         '[[:space:]]*[×xX*][[:space:]]*[0-9]+([.][0-9]+)?[[:space:]]*$',
#         ''
#     ))) = LOWER(p.modifier_name)
#     GROUP BY s.sale_id
# ),
# base_consumption AS (
#     SELECT COALESCE(SUM(s.qty * r.quantity), 0) AS amount
#     FROM sales_data s
#     JOIN ingredient_recipes r ON s.sku = r.sku
# ),
# extra_consumption AS (
#     SELECT COALESCE(
#         SUM(s.qty * COALESCE(r.quantity, t.quantity) * m.extra_qty),
#         0
#     ) AS amount
#     FROM sales_data s
#     JOIN modifier_extras m ON s.sale_id = m.sale_id
#     LEFT JOIN ingredient_recipes r ON s.sku = r.sku
#     CROSS JOIN topping_unit t
# )
# SELECT
#     b.amount AS base_consumption,
#     e.amount AS extra_consumption,
#     b.amount + e.amount AS total_consumption
# FROM base_consumption b
# CROSS JOIN extra_consumption e;
# """
