from pathlib import Path

import pandas as pd

PROCESSED_FILE = Path("processed_files.txt")

def load_processed_files():
    if not PROCESSED_FILE.exists():
        return set()

    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def mark_file_as_processed(file_path):
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(str(Path(file_path).resolve()) + "\n")


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