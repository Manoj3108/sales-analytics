from flask import Flask, jsonify, request
import pandas as pd
from sqlalchemy import create_engine
import os

app = Flask(__name__)

# ---------- DATABASE CONFIG ----------
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "salesdb")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# -------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Sales Analytics API is running",
        "endpoints": [
            "/sales",
            "/sales_filtered",
            "/kpi",
            "/kpi_filtered",
            "/summary/country",
            "/summary/country_filtered",
            "/summary/year",
            "/summary/productline",
            "/summary/productline_filtered",
            "/summary/dealsize",
            "/summary/status",
            "/summary/month",
            "/summary/month_filtered"
        ]
    })

# -------------------------------------------------
@app.route("/sales")
def get_sales():
    query = """
        SELECT *
        FROM sales
        ORDER BY "ORDERDATE" DESC
        LIMIT 100;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/sales_filtered")
def sales_filtered():
    year = request.args.get("year")
    country = request.args.get("country")

    filters = []
    if year:
        filters.append(f'"YEAR_ID" = {year}')
    if country:
        filters.append(f'"COUNTRY" = \'{country}\'')

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT *
        FROM sales
        {where_clause}
        ORDER BY "ORDERDATE" DESC;
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/kpi")
def kpi_metrics():
    query = """
        SELECT 
            ROUND(SUM("SALES")::numeric, 2) AS total_revenue,
            COUNT(DISTINCT "ORDERNUMBER") AS total_orders,
            ROUND(AVG("SALES")::numeric, 2) AS avg_order_value
        FROM sales;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/kpi_filtered")
def kpi_filtered():
    year = request.args.get("year")
    country = request.args.get("country")

    filters = []
    if year:
        filters.append(f'"YEAR_ID" = {year}')
    if country:
        filters.append(f'"COUNTRY" = \'{country}\'')

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT 
            ROUND(SUM("SALES")::numeric, 2) AS total_revenue,
            COUNT(DISTINCT "ORDERNUMBER") AS total_orders,
            ROUND(AVG("SALES")::numeric, 2) AS avg_order_value
        FROM sales
        {where_clause};
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/country")
def summary_country():
    query = """
        SELECT 
            "COUNTRY" AS country,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        GROUP BY "COUNTRY"
        ORDER BY total_sales DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/country_filtered")
def summary_country_filtered():
    year = request.args.get("year")
    country = request.args.get("country")
    top_n = request.args.get("top_n", 10)

    filters = []
    if year:
        filters.append(f'"YEAR_ID" = {year}')
    if country:
        filters.append(f'"COUNTRY" = \'{country}\'')

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT 
            "COUNTRY" AS country,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        {where_clause}
        GROUP BY "COUNTRY"
        ORDER BY total_sales DESC
        LIMIT {int(top_n)};
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/year")
def summary_year():
    query = """
        SELECT 
            "YEAR_ID" AS year,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        GROUP BY "YEAR_ID"
        ORDER BY year;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/productline")
def summary_productline():
    query = """
        SELECT 
            "PRODUCTLINE" AS productline,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        GROUP BY "PRODUCTLINE"
        ORDER BY total_sales DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/productline_filtered")
def summary_productline_filtered():
    year = request.args.get("year")
    country = request.args.get("country")
    top_n = request.args.get("top_n", 10)

    filters = []
    if year:
        filters.append(f'"YEAR_ID" = {year}')
    if country:
        filters.append(f'"COUNTRY" = \'{country}\'')

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT 
            "PRODUCTLINE" AS productline,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        {where_clause}
        GROUP BY "PRODUCTLINE"
        ORDER BY total_sales DESC
        LIMIT {int(top_n)};
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/dealsize")
def summary_dealsize():
    query = """
        SELECT 
            "DEALSIZE" AS dealsize,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        GROUP BY "DEALSIZE"
        ORDER BY total_sales DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/status")
def summary_status():
    query = """
        SELECT 
            "STATUS" AS status,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        GROUP BY "STATUS"
        ORDER BY total_sales DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/month")
def summary_month():
    query = """
        SELECT 
            "YEAR_ID" AS year,
            "MONTH_ID" AS month,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        GROUP BY "YEAR_ID", "MONTH_ID"
        ORDER BY "YEAR_ID", "MONTH_ID";
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df.to_json(orient="records")

# -------------------------------------------------
@app.route("/summary/month_filtered")
def summary_month_filtered():
    year = request.args.get("year")
    country = request.args.get("country")

    filters = []
    if year:
        filters.append(f'"YEAR_ID" = {year}')
    if country:
        filters.append(f'"COUNTRY" = \'{country}\'')

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT 
            "YEAR_ID" AS year,
            "MONTH_ID" AS month,
            ROUND(SUM("SALES")::numeric, 2) AS total_sales
        FROM sales
        {where_clause}
        GROUP BY "YEAR_ID", "MONTH_ID"
        ORDER BY "YEAR_ID", "MONTH_ID";
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df.to_json(orient="records")

@app.route("/healthz")
def health():
    return {"status": "ok"}



# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
