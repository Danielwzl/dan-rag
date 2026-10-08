import pandas as pd

def select_columns(df: pd.DataFrame, REQUIRED_COLUMNS: list[str]) -> pd.DataFrame:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return df[REQUIRED_COLUMNS].copy()


def clean_text_columns(df: pd.DataFrame, TEXT_COLUMNS: list[str]) -> pd.DataFrame:
    for column in TEXT_COLUMNS:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return df


def clean_numeric_columns(df: pd.DataFrame, NUMERIC_COLUMNS: list[str]) -> pd.DataFrame:
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df

def clean_columns(df):
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[%\s]+", "_", regex=True)
          .str.replace(r"_+", "_", regex=True)
          .str.strip("_")
    )
    return df

def strip_symbols(df, cols, symbols=r"[\$,%,]"):
    for c in cols:
        df[c] = (
            df[c].astype(str)
                 .str.replace(symbols, "", regex=True)
                 .str.strip()
                 .replace({"": None, "nan": None})
        )
    return df


def clean_sales_data(df: pd.DataFrame, REQUIRED_COLUMNS: list[str], TEXT_COLUMNS: list[str] = None, NUMERIC_COLUMNS: list[str] = None) -> pd.DataFrame:
    df = select_columns(df, REQUIRED_COLUMNS)
    df = clean_text_columns(df, TEXT_COLUMNS or REQUIRED_COLUMNS)
    df = clean_numeric_columns(df, NUMERIC_COLUMNS or REQUIRED_COLUMNS)

    return df

def clean_data(df: pd.DataFrame, cols) -> pd.DataFrame:
    df = strip_symbols(df, cols)
    df = clean_columns(df)

    return df