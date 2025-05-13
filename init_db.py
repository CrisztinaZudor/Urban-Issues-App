from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData
import datetime
import os

# Make sure folder exists
os.makedirs("data", exist_ok=True)

# Connect to the correct DB
engine = create_engine("sqlite:///data/reports.db")
metadata = MetaData()

# Create the reports table
reports = Table("reports", metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=datetime.datetime.utcnow),
    Column("cracks", Integer),
    Column("fallen_trees", Integer),
    Column("graffiti", Integer),
    Column("illegal_parking", Integer),
    Column("open_manhole", Integer),
    Column("overflowing_trashbin", Integer),
    Column("pothole", Integer),
    Column("stray", Integer),
    Column("trash", Integer),
    Column("roadkills", Integer),
    Column("flood", Integer),
    Column("broken_urban_furniture", Integer),
    Column("wild_animals", Integer),
    Column("dangerous_buildings", Integer),
    Column("location", String),
    Column("description", String),
    Column("status", String)
)

metadata.create_all(engine)
print("✅ Baza de date a fost creată cu succes.")
