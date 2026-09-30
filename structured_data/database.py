import duckdb
import pandas as pd


DB_PATH = "sales.duckdb"


def create_database(df: pd.DataFrame):
    connection = duckdb.connect(DB_PATH)

    connection.register("sales_dataframe", df)

    connection.execute("""
        CREATE OR REPLACE TABLE sales AS
        SELECT *
        FROM sales_dataframe
    """)

    connection.close()


def execute_query(sql):
    connection = duckdb.connect(DB_PATH)

    result = connection.execute(sql).fetchdf()

    connection.close()

    return result