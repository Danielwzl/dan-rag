from structured_data.database import execute_query
from structured_data.database import show_all_data


sql_count_same_group  = """
    SELECT
        r.group as group_name, COUNT(*) as item_count
    FROM menu_items r
    JOIN sales s 
        ON r.sku = s.sku
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


# sql = """
# SELECT
#   *
# FROM menu_items;
# """



result = execute_query(sql)

print(result)
result.to_csv("output_file2.csv", index=False)
# data = show_all_data("sales")

# print(data)