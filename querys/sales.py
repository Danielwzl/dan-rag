from structured_data.database import execute_query
from structured_data.database import show_all_data

sql_count_same_group  = """
    SELECT
        r.group as group_name, COUNT(*) as item_count
    FROM menu_items r
    JOIN sales s 
        ON r.sku = s.sku
    WHERE s."date" >= '2026-09-14' AND s."date" < '2026-09-27'
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

result = execute_query(sql_count_same_group)

print(result)
result.to_csv("count_same_group.csv", index=False)