# -*- coding: utf-8 -*-
"""
Created on Sat May 10 19:32:16 2025

@author: Zinveliu Ioana
"""

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData
import datetime

engine = create_engine("sqlite:///data.db")
metadata = MetaData()

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

metadata.create_all(engine)
print("Baza de date a fost creată.")
