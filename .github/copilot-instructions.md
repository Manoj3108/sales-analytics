# AI Coding Instructions for Sales Analytics

## Architecture Overview

This is a **multi-service Docker-based analytics platform** with four components:

- **PostgreSQL Database** (`db`): Centralized data store containing a single `sales` table
- **CSV Loader** (`loader`): One-time startup service that loads `data/sales_data.csv` into PostgreSQL
- **Flask API** (`api:5000`): REST API providing aggregated sales metrics and filtered queries
- **Streamlit Dashboard** (`dashboard:8501`): Interactive UI consuming the Flask API

**Service startup order** (defined in `docker-compose.yml`):
1. DB starts first (health-checked with `pg_isready`)
2. Loader waits for DB health, then completes
3. API waits for both loader success and DB health
4. Dashboard depends only on API being started

## Data Flow & Column Normalization

All column names in the `sales` table are **UPPERCASE** (normalized in [load_data.py](../load_data.py#L11-L12)):
- CSV columns are normalized: `df.columns = [c.upper() for c in df.columns]`
- SQL queries **must** use quoted uppercase: `"COUNTRY"`, `"YEAR_ID"`, `"SALES"`, `"ORDERDATE"`, etc.
- The dashboard handles string encoding issues from the Windows-encoded CSV (see [dashboard.py#L17-L18](dashboard.py#L17-L18))

## API Endpoints Pattern

The Flask API ([app.py](../app.py)) follows a consistent pattern:

1. **Unfiltered endpoints** (e.g., `/summary/country`, `/summary/year`):
   - Return aggregated data grouped by a dimension
   - Use `to_json(orient="records")` format
   - No query parameters

2. **Filtered endpoints** (e.g., `/kpi_filtered`, `/sales_filtered`):
   - Accept optional `year` and `country` query parameters: `?year=2003&country=USA`
   - Build WHERE clause dynamically from filters
   - Some include `top_n` parameter (default 10) to limit grouped results

3. **KPI endpoints** (`/kpi`, `/kpi_filtered`):
   - Return: `total_revenue`, `total_orders`, `avg_order_value` (rounded to 2 decimals)

## Dashboard Filter Mechanics

The Streamlit dashboard ([dashboard.py](dashboard.py)) implements a **cascading filter pattern**:
- Filters load static metadata (`year_df`, `country_df_static`) first
- User selections build query strings: `?year=2003&country=USA&top_n=10`
- Same query string applied to both filtered and summary endpoints
- All dashboard charts use `set_index()` for proper display

## Critical Developer Workflows

### Build & Run Everything
```
docker compose up --build -d
```
- Rebuilds all images and starts services in dependency order
- Dashboard available at `http://localhost:8501`
- API available at `http://localhost:5000`

### Reset Database + Reload Data
```
docker compose down -v
docker compose up --build -d
```
The `-v` flag removes persistent PostgreSQL volumes, forcing a fresh reload.

### Test API Locally (without Docker)
```
# Install: pip install -r requirements-api.txt
# Assuming local PostgreSQL at 127.0.0.1:5432
python app.py
```
[db_load.py](../db_load.py) is the legacy local loader; use [load_data.py](../load_data.py) for Docker.

## Environment Configuration

All services inherit database credentials from `docker-compose.yml`:
```
DB_HOST: db (service name inside Docker network)
POSTGRES_DB: salesdb
POSTGRES_USER: postgres
POSTGRES_PASSWORD: admin
```

For local development, [db_load.py](db_load.py) uses `DB_HOST=127.0.0.1` and explicit port 5432.

## Common Patterns to Apply

- **Filter building**: Conditionally append WHERE clauses only if filters exist (avoid empty WHERE)
- **Numeric rounding**: Always use `ROUND(value::numeric, 2)` in SQL to prevent floating-point issues
- **JSON serialization**: Use `df.to_json(orient="records")` for all API responses
- **Column case safety**: Use quoted UPPERCASE for all column references in SQL to match normalized schema

## Key Files Reference

- **Data schema & load logic**: [load_data.py](../load_data.py)
- **All API endpoints**: [app.py](../app.py)
- **Dashboard UI & filter logic**: [dashboard.py](../dashboard.py)
- **Service orchestration**: [docker-compose.yml](../docker-compose.yml)
- **Per-service dependencies**: `requirements-api.txt`, `requirements-ui.txt`, `requirements-loader.txt`
