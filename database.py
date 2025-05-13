
import sqlite3

# Calea către baza de date SQLite
DB_PATH = "data/reports.db"

# Funcție pentru a crea baza de date și tabelul (dacă nu există)
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        cracks INTEGER,
        fallen_trees INTEGER,
        graffiti INTEGER,
        illegal_parking INTEGER,
        open_manhole INTEGER,
        overflowing_trashbin INTEGER,
        pothole INTEGER,
        stray INTEGER,
        trash INTEGER,
        roadkills INTEGER,
        flood INTEGER,
        broken_urban_furniture INTEGER,
        wild_animals INTEGER,
        dangerous_buildings INTEGER,
        location TEXT,
        description TEXT,
        status TEXT
    )''')

    conn.commit()
    conn.close()


# Funcție pentru a salva un raport în baza de date
def save_report(report_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    CLASS_NAMES = [
        "cracks", "fallen_trees", "graffiti", "illegal_parking", "open_manhole",
        "overflowing_trashbin", "pothole", "stray", "trash", "roadkills",
        "flood", "broken_urban_furniture", "wild_animals", "dangerous_buildings"
    ]

    columns = ", ".join(CLASS_NAMES)
    placeholders = ", ".join(["?"] * len(CLASS_NAMES))
    values = [report_data.get(cls, 0) for cls in CLASS_NAMES]

    cursor.execute(f'''
        INSERT INTO reports (timestamp, {columns}, location, description, status)
        VALUES (?, {placeholders}, ?, ?, ?)
    ''', [report_data["Timestamp"]] + values + [report_data["Location"], report_data["Description"], report_data["Status"]])

    conn.commit()
    conn.close()


# Funcție pentru a obține toate rapoartele din baza de date
def get_reports():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports")
    rows = cursor.fetchall()
    
    conn.close()
    return rows
