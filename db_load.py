import pandas as pd
from sqlalchemy import create_engine

# ---------- DATABASE CONFIG ----------
DB_USER = "postgres"
DB_PASSWORD = "admin"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "salesdb"
# -------------------------------------

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Load CSV (Windows encoding safe)
df = pd.read_csv("data/sales_data.csv", encoding="cp1252")

print("CSV loaded. Rows:", len(df))
print("Columns:", list(df.columns))

# Normalize column names (IMPORTANT)
df.columns = [c.strip().upper() for c in df.columns]

# Parse date column safely
if "ORDERDATE" in df.columns:
    df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], errors="coerce")

# Write fresh table
df.to_sql("sales", engine, if_exists="replace", index=False)

print("✅ Database reset complete. Data reloaded into PostgreSQL.")
