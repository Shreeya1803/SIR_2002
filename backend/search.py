import sqlite3
import json
from database import DB_PATH


def search_records(query, limit=50):
    """
    Searches the database for records matching the Marathi query.

    Args:
        query: Marathi search term e.g. "रामचंद्र"
        limit: Max number of results to return (default 50)

    Returns:
        List of dicts e.g. [{"नाव": "रामचंद्र", "गाव": "पुणे"}, ...]
    """

    conn = sqlite3.connect(DB_PATH)

    # row_factory makes each database row behave like a dictionary
    # so we can access columns by name: row["data"] instead of row[0]
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    try:
        # Add * for prefix/wildcard matching.
        # "राम*" matches रामचंद्र, रामदास, रामेश्वर etc.
        # Without *, only exact whole-word matches work.
        fts_query = query.strip() + "*"

        cur.execute("""
            SELECT r.data, s.columns
            FROM records r
            JOIN records_fts fts ON r.id = fts.rowid
            JOIN sheets s ON r.sheet_id = s.id
            WHERE records_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, limit))

        results = []
        for row in cur.fetchall():

            # row["data"] is a JSON string like:
            # '{"नाव": "रामचंद्र", "गाव": "पुणे"}'
            # json.loads converts it back to a Python dictionary
            data = json.loads(row["data"])

            # row["columns"] is a JSON string like:
            # '["नाव", "गाव", "पद", "मोबाईल"]'
            columns = json.loads(row["columns"])

            # Build result dict with columns in the ORIGINAL order
            # (the order they appeared in the Excel file)
            ordered_result = {col: data.get(col, "") for col in columns}
            results.append(ordered_result)

    except Exception as e:
        # If the query has special FTS5 characters like * - ( )
        # it can cause a syntax error. We catch it and return empty.
        print(f"Search error for query '{query}': {e}")
        results = []

    finally:
        # Always close the connection, even if an error occurred
        conn.close()

    return results