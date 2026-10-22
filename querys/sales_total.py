from structured_data.database import execute_query
from structured_data.database import show_all_data

sql  = """
WITH detail_data AS (
    SELECT
       COALESCE(r.name, s.item) AS group_name, COUNT(*) as item_count
    FROM menu_items r
    RIGHT JOIN sales s 
        ON CASE
            WHEN s.sku IS NULL OR TRIM(s.sku) = ''
                THEN TRIM(s.item) = TRIM(r.name)
            ELSE TRIM(CAST(s.sku AS VARCHAR)) = TRIM(CAST(r.sku AS VARCHAR))
        END
    WHERE CAST(s."date" AS DATE) BETWEEN '2026-09-14' AND '2026-10-18' AND group_name LIKE '%Strawb%'
    GROUP BY group_name
)

SELECT * FROM
(SELECT group_name, item_count
FROM detail_data

UNION ALL

SELECT 'TOTAL' AS group_name, SUM(item_count) AS item_count
FROM detail_data)

ORDER BY
    CASE WHEN group_name = 'TOTAL' THEN 1 ELSE 0 END,
    item_count DESC
    ;
"""

result = execute_query(sql)

print(result)
result.to_csv("sales_in_total.csv", index=False)