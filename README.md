# मराठी डेटा शोध — Marathi Data Search App

A mobile-based data management and search system for handling large volumes of structured data stored in Excel files containing **Marathi language content**.

---

## What This App Does

This app allows administrators to upload multiple Excel sheets containing Marathi data, automatically stores all records in a centralized database, and provides fast and accurate search so users can find any record instantly by typing a Marathi name or keyword.

Search results are displayed in a clean **column name: value** format:

```
नाव: रामचंद्र शिंदे
गाव: पुणे
पद: अध्यक्ष
मोबाईल: 9876543210
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile App | React Native (Expo) |
| Backend Server | Python + Flask |
| Database | SQLite with FTS5 full-text search |
| Excel Parsing | pandas + openpyxl |
| Search | SQLite FTS5 with `unicode61` tokenizer (Marathi-aware) |
| HTTP Client | Axios |
| Navigation | React Navigation (Bottom Tabs) |

---

## Features

- Upload multiple `.xlsx` / `.xls` Excel files from your phone
- Automatically extracts Marathi column names and all row data
- Full-text search across all uploaded files simultaneously
- Prefix/wildcard search — typing `राम` finds `रामचंद्र`, `रामदास`, etc.
- Results displayed as cards with `column name: value` layout
- View list of all uploaded files with upload timestamps
- Long-press to delete any uploaded sheet and its records
- Works entirely on local Wi-Fi — no internet required
- Unicode-aware search correctly handles Devanagari script

---

## Project Structure

```
marathi-app/
├── backend/                  # Python Flask server
│   ├── main.py               # API server — all routes
│   ├── database.py           # SQLite setup and table creation
│   ├── parser.py             # Excel file reading with pandas
│   ├── search.py             # FTS5 full-text search logic
│   ├── requirements.txt      # Python dependencies
│   └── uploads/              # Uploaded Excel files stored here
│
└── MarathiApp/               # React Native mobile app
    ├── App.js                # Root file — navigation setup
    ├── src/
    │   ├── api.js            # All backend API calls
    │   └── screens/
    │       ├── SearchScreen.js   # Search UI and result cards
    │       └── UploadScreen.js   # File upload and sheet list
    └── assets/
        ├── icon.png          # App icon (1024×1024)
        └── splash.png        # Splash screen
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload an Excel file |
| `GET` | `/search?q=राम` | Search records with Marathi keyword |
| `GET` | `/sheets` | List all uploaded sheets |
| `DELETE` | `/sheets/<id>` | Delete a sheet and all its records |

---

## Getting Started

### Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- Expo Go app on your Android or iPhone
- Both phone and laptop on the same Wi-Fi network

---

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd marathi-app
```

---

### 2. Set up the backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The server will start and show your local IP address:

```
* Running on http://192.168.X.X:5000
```

**Note this IP address** — you will need it in the next step.

---

### 3. Set up the mobile app

Open a second terminal window:

```bash
cd MarathiApp

# Install packages
npm install

# Update the backend IP address
# Open src/api.js and change BASE_URL to your IP from step 2:
# const BASE_URL = 'http://192.168.X.X:5000';

# Start the app
npx expo start
```

Scan the QR code with Expo Go (Android) or the Camera app (iPhone).

---

## How to Use

### Upload data
1. Tap the **अपलोड** tab at the bottom
2. Tap **"Excel फाइल निवडा आणि अपलोड करा"**
3. Pick your `.xlsx` file — it uploads and imports all rows automatically

### Search
1. Tap the **शोध** tab
2. Type any Marathi name or keyword (minimum 2 characters)
3. Results appear instantly as cards showing all column data

### Delete a sheet
1. Go to the **अपलोड** tab
2. Long-press any sheet in the list
3. Confirm deletion — all records from that sheet are removed

---

## Excel File Format

Your Excel file can have any Marathi column names. Example:

| नाव | गाव | पद | मोबाईल |
|---|---|---|---|
| रामचंद्र शिंदे | पुणे | अध्यक्ष | 9876543210 |
| सुनील पाटील | नाशिक | सदस्य | 9123456789 |

- First row must be column headers
- All cells are read as text (phone numbers stay as-is)
- Empty cells are handled gracefully
- Multiple sheets in one file: first sheet is read by default

---

## Database Schema

```sql
-- Tracks each uploaded Excel file
CREATE TABLE sheets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    filename    TEXT NOT NULL,
    columns     TEXT NOT NULL,        -- JSON array of column names
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Stores every row from every Excel file
CREATE TABLE records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sheet_id    INTEGER REFERENCES sheets(id),
    data        TEXT NOT NULL,        -- JSON: {"नाव": "राम", "गाव": "पुणे"}
    search_text TEXT NOT NULL         -- All values merged for FTS
);

-- Full-text search index with Marathi Unicode support
CREATE VIRTUAL TABLE records_fts USING fts5(
    search_text,
    content='records',
    tokenize='unicode61'              -- Handles Devanagari script correctly
);
```

---

## Configuration

### Changing the backend port

In `backend/main.py`, change the last line:

```python
app.run(host="0.0.0.0", port=5001, debug=True)  # change 5000 to any free port
```

Update `src/api.js` in the app to match:

```javascript
const BASE_URL = 'http://192.168.X.X:5001';
```

### Changing search result limit

In `backend/search.py`:

```python
def search_records(query, limit=50):  # increase for more results
```

---

## Troubleshooting

**App cannot connect to backend**
- Confirm phone and laptop are on the same Wi-Fi network
- Check the IP in `src/api.js` matches what `python main.py` shows
- Make sure the backend terminal is still running
- On Windows, allow Python through the firewall when prompted

**Marathi text appears garbled**
- Every `json.dumps()` call in the backend must include `ensure_ascii=False`
- This is already set correctly in the provided code

**Search returns no results**
- Try typing fewer characters — the search uses prefix matching
- Verify data was imported: check the अपलोड tab for the file listing
- Confirm the backend is running and reachable

**`venv\Scripts\activate` is disabled on Windows**
- Run PowerShell as Administrator and execute:  
  `Set-ExecutionPolicy RemoteSigned`

**Port 5000 already in use**
- Run `netstat -ano | findstr :5000` to find the process
- Or simply change the port to 5001 in `main.py`

---

## License

[MIT](LICENSE)

---

## Acknowledgements

- [pandas](https://pandas.pydata.org/) — Excel file parsing
- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [Expo](https://expo.dev/) — React Native toolchain
- [SQLite FTS5](https://www.sqlite.org/fts5.html) — Full-text search engine
- [Noto Sans Devanagari](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari) — Marathi font
