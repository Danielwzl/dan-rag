import csv

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = "data/Full Menu Update - Ingredients_modified.csv"
OUTPUT_FILE = "recipe_data.csv"

# Ingredient columns start from column 7
# Python index 6
INGREDIENT_START = 6


# ============================================================
# READ CSV
# ============================================================

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as file:
    rows = list(csv.reader(file))


# ============================================================
# GET INGREDIENT NAMES
# ============================================================

# Row 0:
# columns 6 onward = ingredient names
ingredient_names = rows[0][INGREDIENT_START:]


# ============================================================
# EXTRACT RECIPE
# ============================================================

recipe_data = []

# Row 1 is the header
# Row 2 onward are menu records
for row in rows[2:]:

    # Name is column 2 -> Python index 1
    menu_name = row[1].strip()

    # Skip blank rows
    if not menu_name:
        continue

    # Check every ingredient column
    for i, ingredient_name in enumerate(ingredient_names):

        ingredient_name = ingredient_name.strip()

        if not ingredient_name:
            continue

        # Convert relative index to real CSV column
        column_index = INGREDIENT_START + i

        value = row[column_index].strip()

        # Empty = this menu does not use the ingredient
        if value == "":
            continue

        # Convert quantity
        try:
            quantity = float(value)
        except ValueError:
            continue

        # Ignore 0
        if quantity == 0:
            continue

        recipe_data.append([
            menu_name,
            ingredient_name,
            quantity
        ])


# ============================================================
# WRITE OUTPUT
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8-sig",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "menu_name",
        "ingredient_name",
        "quantity"
    ])

    writer.writerows(recipe_data)


# ============================================================
# PRINT RESULT
# ============================================================

print(f"Total recipe records: {len(recipe_data)}")
print(f"Output: {OUTPUT_FILE}")

print("\nFirst 20 records:\n")

for row in recipe_data[:20]:
    print(row)