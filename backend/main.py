from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
import tempfile

from database import init_db, DB_PATH
from parser import parse_excel
from search import search_records

def normalize_key(key):
    return key.strip().lower().replace(" ", "").replace(".", "")

# Create app
app = Flask(__name__)
CORS(app)

# 🔥 Limit file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Init DB
init_db()

# 🔥 FIXED COLUMN ORDER
COLUMN_MAPPING = [
    "Epic No.",
    "Junnar",
    "Booth No(2024)",
    "Sr no.(2024)",
    "Full Name",
    "Part No(2002)",
    "Serial No (2002)",
    "Relation Name",
    "Relation Type",
    "Gender",
    "Age",
    "Voter ID",
    "House No"
]

# ─────────────────────────────────────────
# 📂 UPLOAD EXCEL (FIXED)
# ─────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload():

    # 🔍 Debug logs (IMPORTANT)
    print("FILES:", request.files)

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # 🔥 FIX: Remove strict extension check
    if file.filename == "":
        return jsonify({"error": "Invalid file"}), 400

    try:
        # 🔥 Use temp file (Render-safe)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            file.save(tmp.name)
            filepath = tmp.name

        # Parse Excel
        columns, rows = parse_excel(filepath)

        # DB insert
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO sheets (filename, columns) VALUES (?, ?)",
            (file.filename, json.dumps(columns, ensure_ascii=False))
        )
        sheet_id = cur.lastrowid

        for row in rows:
            data_json = json.dumps(row, ensure_ascii=False)
            search_text = " ".join(str(v) for v in row.values() if v)

            cur.execute(
                "INSERT INTO records (sheet_id, data, search_text) VALUES (?, ?, ?)",
                (sheet_id, data_json, search_text)
            )

        conn.commit()
        conn.close()

        # Cleanup temp file
        os.remove(filepath)

        return jsonify({
            "success": True,
            "rows_imported": len(rows),
            "columns": columns
        })

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ─────────────────────────────────────────
# 🔍 SEARCH
# ─────────────────────────────────────────
@app.route("/search", methods=["GET"])
def search():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    results = search_records(query)

    formatted_results = []

    for record in results:
        formatted_record = {}

        for col in COLUMN_MAPPING:
            value = ""

            for key in record.keys():
                if normalize_key(key) == normalize_key(col):
                    value = record[key]
                    break

            formatted_record[col] = value

        formatted_results.append(formatted_record)

    return jsonify(formatted_results)


# ─────────────────────────────────────────
# 📋 LIST SHEETS
# ─────────────────────────────────────────
@app.route("/sheets", methods=["GET"])
def list_sheets():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT id, filename, uploaded_at FROM sheets ORDER BY uploaded_at DESC"
    )

    sheets = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(sheets)


# ─────────────────────────────────────────
# ❌ DELETE SHEET
# ─────────────────────────────────────────
@app.route("/sheets/<int:sheet_id>", methods=["DELETE"])
def delete_sheet(sheet_id):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM records WHERE sheet_id = ?", (sheet_id,))
        record_ids = [row[0] for row in cur.fetchall()]

        for rid in record_ids:
            cur.execute("DELETE FROM records_fts WHERE rowid = ?", (rid,))

        cur.execute("DELETE FROM records WHERE sheet_id = ?", (sheet_id,))
        cur.execute("DELETE FROM sheets WHERE id = ?", (sheet_id,))

        conn.commit()

        return jsonify({
            "success": True,
            "deleted_sheet_id": sheet_id
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

    finally:
        conn.close()


# ─────────────────────────────────────────
# 🚀 HEALTH CHECK (IMPORTANT for Render)
# ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "Backend is running ✅"


# ─────────────────────────────────────────
# 🚀 START SERVER
# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )