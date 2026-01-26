import pandas as pd
from sqlalchemy import create_engine
import os
import time

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "salesdb")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL)

print("⏳ Waiting for Postgres to be ready...")
time.sleep(10)

csv_path = "/data/sales_data.csv"
df = pd.read_csv(csv_path, encoding="cp1252")

# normalize column names → lowercase
df.columns = [c.lower() for c in df.columns]

print("📥 Loading CSV into Docker Postgres...")
df.to_sql("sales", engine, if_exists="replace", index=False)

print("✅ sales table created successfully!")
