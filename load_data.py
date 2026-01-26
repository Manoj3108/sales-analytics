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

CSV_PATH = "data/sales_data.csv"

print("⏳ Waiting for Postgres to be ready...")
time.sleep(10)

print("📥 Reading CSV...")
df = pd.read_csv(CSV_PATH)

print("🧹 Normalizing column names to UPPERCASE...")
df.columns = [c.upper() for c in df.columns]

print("🗄 Writing data to Postgres (table = sales)...")
df.to_sql("sales", engine, if_exists="replace", index=False)

print("✅ Sales table created and data loaded successfully!")
print(f"📊 Rows inserted: {len(df)}")
