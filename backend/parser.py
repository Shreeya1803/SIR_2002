import pandas as pd

def parse_excel(filepath):
    """
    Reads an Excel file and returns:
      - columns: list of column names (e.g. ["नाव", "गाव", "पद"])
      - rows: list of dicts (e.g. [{"नाव": "राम", "गाव": "पुणे"}, ...])
    """

    # dtype=str → read every cell as plain text.
    # Without this, pandas converts numbers to floats:
    # "9876543210" becomes 9876543210.0 which looks wrong.
    df = pd.read_excel(filepath, dtype=str)

    # Replace empty cells (NaN) with empty string "".
    # NaN causes errors when converting to JSON later.
    df.fillna("", inplace=True)

    # Extract column names from the first row of the Excel file.
    # These will be your Marathi headers like नाव, गाव, पद etc.
    columns = list(df.columns)

    # Convert each row into a dictionary.
    # orient="records" means: one dict per row, keys are column names.
    rows = df.to_dict(orient="records")

    return columns, rows