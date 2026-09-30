from structured_data.loader import load_file
from structured_data.database import create_database


DATA_FILE = "data/items-2026-09-27-2026-10-04.csv"


df = load_file(DATA_FILE)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")

print("\nFirst 5 rows:")
print(df.head())

create_database(df)

print("\nSales database created.")