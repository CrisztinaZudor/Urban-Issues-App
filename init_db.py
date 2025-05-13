from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData
import datetime
import os

# Ensure the 'data' folder exists
os.makedirs("data", exist_ok=True)

# Create engine for the correct path
engine = create_engine("sqlite:///data/reports.db")
metadata = MetaData()

# Define the table
reports = Table("reports", metadata,
    Column("id", Integer, primary_key=True),
    Column("description", String),
    Column("location", String),
    Column("status", String),
    Column("timestamp", DateTime, default=datetime.datetime.utcnow),
    Column("potholes", String),
    Column("parking", String),
    Column("graffiti", String),
    Column("overflow", String)
)

# Create the table if it doesn't exist
metadata.create_all(engine)
print("Baza de date a fost creată.")
