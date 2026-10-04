from structured_data.database import execute_many
from pathlib import Path
from dotenv import load_dotenv
import os
import json

load_dotenv()
raw_path = os.getenv("INGREDIENTS_FILE_PATH")

if not raw_path:
    raise ValueError("Security Error: INGREDIENTS_FILE_PATH is not set in the environment!")

file_path = Path(raw_path)

with open(file_path, "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    # Convert lists back to tuples if you need exact matching structure
    loaded_ingredients = [tuple(item) for item in loaded_data]

def insert_ingredients_names():
    execute_many("""
        INSERT INTO ingredients_names (
            category,
            ingredient_name,
            cost_per_kg
        )
        VALUES (?, ?, ?)
    """, loaded_ingredients)