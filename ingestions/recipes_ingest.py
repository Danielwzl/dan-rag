from structured_data.loader import load_file
from structured_data.database import create_table_with_data


DATA_FILE = "data/metadata/recipes.csv"


df = load_file(DATA_FILE)

df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(r"\s+", "_", regex=True)
)

df = df.fillna("")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")

print("\nFirst 5 rows:")
print(df.head())

create_table_with_data(df, "recipes")

print("\ndatabase created.")