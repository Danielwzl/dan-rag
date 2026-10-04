from structured_data.database import execute_query


sql = """
SELECT
    *
FROM ingredients_names
"""

result = execute_query(sql)

print(result)