from structured_data.loader import load_file
from structured_data.database import create_database
from structured_data.data_cleaning import clean_sales_data


DATA_FILE = "data/items-2026-09-27-2026-10-04.csv"

REQUIRED_COLUMNS = [
    "Date",
    "Time",
    "Category",
    "Item",
    "Qty",
    "Price Point Name",
    "SKU",
    "Modifiers Applied",
    "Gross Sales",
    "Discounts",
    "Net Sales",
    "Tax",
    "Device Name",
    "Event Type",
    "Location",
    "Unit",
    "Count",
    "Card Brand"
]

df = load_file(DATA_FILE)

df = clean_sales_data(df, REQUIRED_COLUMNS, [e for e in REQUIRED_COLUMNS if e not in {"Qty", "Count"}], ["Qty", "Count"])

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
for column in df.columns:
    print(f"- {column}")

print("\nFirst 5 rows:")
print(df.head())

create_database(df)

print("\nSales database created.")