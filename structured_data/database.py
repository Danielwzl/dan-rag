import duckdb
import pandas as pd


DB_PATH = "sales.duckdb"

def create_table_ingredients_names():
    connection = duckdb.connect(DB_PATH)
    connection.execute("CREATE OR REPLACE SEQUENCE user_id_seq START 1;")
    connection.execute("""
        CREATE OR REPLACE TABLE ingredients_names(
            id INTEGER PRIMARY KEY DEFAULT nextval('user_id_seq'),
            category VARCHAR,
            ingredient_name VARCHAR,
            cost_per_kg DOUBLE
        )
    """)

    connection.close()


def create_table_with_data(df: pd.DataFrame, table_name: str):
    connection = duckdb.connect(DB_PATH)

    connection.register("temp_dataframe", df)

    connection.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM temp_dataframe
    """)

    connection.close()

def show_all_data(table: str):
    connection = duckdb.connect(DB_PATH)
    result = connection.sql(f"SELECT * FROM {table}").fetchdf()
    pd.set_option('display.max_columns', None)       # Show all columns without truncation
    pd.set_option('display.width', 1000)             # Force the line length limit to 1000 characters
    pd.set_option('display.expand_frame_repr', False) # Prevent wrapping columns to new lines
    connection.close()

    return result


def execute_query(sql):
    connection = duckdb.connect(DB_PATH)

    result = connection.execute(sql).fetchdf()

    connection.close()

    return result

def execute_many(sql, data: []):
    connection = duckdb.connect(DB_PATH)

    result = connection.executemany(sql, data)

    connection.close()

    return result