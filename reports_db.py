import sqlite3
import os

# Path to your database file
DB_PATH = os.path.join("data", "reports.db")

# Initialize the database and create the table if it doesn't exist
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
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
        )
    ''')
    conn.commit()
    conn.close()

# Save a new report to the database
def insert_report(report):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports (
            timestamp, cracks, fallen_trees, graffiti, illegal_parking, open_manhole,
            overflowing_trashbin, pothole, stray, trash, roadkills, flood,
            broken_urban_furniture, wild_animals, dangerous_buildings,
            location, description, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report["timestamp"], report["cracks"], report["fallen_trees"], report["graffiti"],
        report["illegal_parking"], report["open_manhole"], report["overflowing_trashbin"],
        report["pothole"], report["stray"], report["trash"], report["roadkills"], report["flood"],
        report["broken_urban_furniture"], report["wild_animals"], report["dangerous_buildings"],
        report["location"], report["description"], report["status"]
    ))
    conn.commit()
    conn.close()

# Fetch all reports as a pandas DataFrame
def fetch_reports():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    conn.close()
    return df
