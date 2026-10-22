from structured_data.database import execute_query
from structured_data.database import show_all_data


sql  = """
    SELECT
       COALESCE(r.group, s.item) AS group_name, COUNT(*) as item_count
    FROM menu_items r
    RIGHT JOIN sales s 
        ON CASE
            WHEN s.sku IS NULL OR TRIM(s.sku) = ''
                THEN TRIM(s.item) = TRIM(r.name)
            ELSE TRIM(CAST(s.sku AS VARCHAR)) = TRIM(CAST(r.sku AS VARCHAR))
        END
    WHERE CAST(s."date" AS DATE) BETWEEN '2025-01-01' AND '2026-01-01' AND s.location = 'Shawnessy'
    GROUP BY group_name
    ORDER BY item_count DESC
    ;
"""

# sql_count_same_group_verify = """
# SELECT 
#     COUNT(*)
# FROM sales
# WHERE sku = 'A1800063' OR sku = 'G01164'
# GROUP BY sku
# ;
# """

# sql_count_same_group = """
# SELECT
#     typeof("Date") AS date_type
# FROM sales;
# """

result = execute_query(sql)

print(result)
result.to_csv("sales_location.csv", index=False)