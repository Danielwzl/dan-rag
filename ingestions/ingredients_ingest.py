from structured_data.loader import load_file
from structured_data.database import create_table_ingredients_names
from structured_data.data_cleaning import clean_sales_data
from structured_data.ingredients.insert_ingredients import insert_ingredients_names


DATA_FILE = "data/Full Menu Update - Ingredients.csv"

df = load_file(DATA_FILE)

# df_reciept = df.iloc[1:]

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")

print("\nFirst 5 rows:")
print(df)

create_table_ingredients_names()

insert_ingredients_names()

print("\nIngredients_names database created.")