from pathlib import Path

import pandas as pd


def load_csv(file_path):
    return pd.read_csv(file_path)


def load_excel(file_path, sheet_name=0):
    return pd.read_excel(
        file_path,
        sheet_name=sheet_name
    )


def load_file(file_path):
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".csv":
        return load_csv(file_path)

    if file_path.suffix.lower() in [".xls", ".xlsx"]:
        return load_excel(file_path)

    raise ValueError(
        f"Unsupported file type: {file_path.suffix}"
    )