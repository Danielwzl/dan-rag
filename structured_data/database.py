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