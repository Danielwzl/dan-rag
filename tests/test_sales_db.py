from structured_data.database import execute_query
from structured_data.database import show_all_data


sql = """
SELECT
    r.group as group_name, COUNT(*) as item_count
FROM menu_items r
JOIN sales s 
    ON r.sku = s.sku
GROUP BY group_name
ORDER BY item_count DESC
;
"""

# sql = """
# SELECT
#     item,
#     COUNT(*) as item_count
# FROM sales
# GROUP BY item
# ORDER BY item_count DESC
# LIMIT 100
# ;
# """



# sql = """
# SELECT
#   *
# FROM menu_items;
# """

# sql = """
# SELECT 
#     quantity,
#     TRY_CAST(quantity AS DOUBLE) IS NOT NULL AS is_number
# FROM recipes;
# """

result = execute_query(sql)

print(result)
result.to_csv("output_file2.csv", index=False)
# data = show_all_data("sales")

# print(data)