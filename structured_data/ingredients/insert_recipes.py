from structured_data.database import execute_many

def insert_recipes(data):
    execute_many("""
        INSERT INTO recipes (
            menu_name,
            ingredient_name,
            sku,
            quantity
        )
        VALUES (?, ?, ?, ?)
    """, data)