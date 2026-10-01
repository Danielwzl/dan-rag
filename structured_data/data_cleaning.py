import pandas as pd


def remove_columns(
    df: pd.DataFrame,
    remove_columns: list[str]
) -> pd.DataFrame:

    existing_columns = [
        column
        for column in remove_columns
        if column in df.columns
    ]

    return df.drop(columns=existing_columns)