from structured_data.loader import load_file
from structured_data.database import create_table_with_data
from structured_data.data_cleaning import clean_data
import re


DATA_FILE = "data/metadata/menu_items.csv"


def get_category(name: str) -> str:
    if not isinstance(name, str):
        return name

    n = name.strip()

    n = re.sub(r"\s*\([LM]\)\s*$", "", n)

    n = re.sub(r"\s+[LM]$", "", n)

    n = re.sub(r"\s+[LM]\s+w/", " w/", n)

    return n.strip()


df = load_file(DATA_FILE)
df["Group"] = df["Name"].apply(get_category)
df = clean_data(df, ["Menu Price", "Food Cost%", "Cost per cup"])

df = df.fillna("")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")

print("\nFirst 5 rows:")
print(df.head())

create_table_with_data(df, "menu_items")

print("\ndatabase created.")



