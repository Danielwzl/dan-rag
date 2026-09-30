from structured_data.database import execute_query


sql = """
SELECT
    *
FROM sales
"""

result = execute_query(sql)

print(result)