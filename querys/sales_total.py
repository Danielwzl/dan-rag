from structured_data.database import execute_query
from structured_data.database import show_all_data

sql  = """
    SELECT
       COALESCE(r.name, s.item) AS group_name, COUNT(*) as item_count
    FROM menu_items r
    RIGHT JOIN sales s 
        ON CASE
            WHEN s.sku IS NULL OR TRIM(s.sku) = ''
                THEN TRIM(s.item) = TRIM(r.name)
            ELSE TRIM(CAST(s.sku AS VARCHAR)) = TRIM(CAST(r.sku AS VARCHAR))
        END
    WHERE CAST(s."date" AS DATE) BETWEEN '2025-01-01' AND '2026-01-01'
    GROUP BY group_name
    ORDER BY item_count DESC
    ;
"""

result = execute_query(sql)

print(result)
result.to_csv("sales_in_total.csv", index=False)