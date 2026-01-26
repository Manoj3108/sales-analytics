import streamlit as st
import pandas as pd
import requests
import streamlit as st


API_BASE_URL = "http://api:5000"



# -------------------------------
def load_data(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url)
    response.raise_for_status()
    df = pd.DataFrame(response.json())

    # 🔧 Fix LargeUtf8 issue
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

    return df



# -------------------------------
st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")
st.title("📊 Sales Analytics Dashboard")


# ===============================
# LOAD STATIC SUMMARY DATA
# ===============================
country_df_static = load_data("/summary/country")
year_df = load_data("/summary/year")
productline_df_static = load_data("/summary/productline")
dealsize_df = load_data("/summary/dealsize")
status_df = load_data("/summary/status")


# ===============================
# FILTER UI
# ===============================
st.sidebar.header("🎛 Filters")

years = sorted(year_df["year"].unique())
countries = sorted(country_df_static["country"].unique())

selected_year = st.sidebar.selectbox("Select Year", ["All"] + list(years))
selected_country = st.sidebar.selectbox("Select Country", ["All"] + list(countries))

top_n = st.sidebar.slider("Top N (for Country & Product Line)", min_value=5, max_value=20, value=10, step=1)


# ===============================
# BUILD QUERY STRING
# ===============================
query_params = []
if selected_year != "All":
    query_params.append(f"year={selected_year}")
if selected_country != "All":
    query_params.append(f"country={selected_country}")

query_string = ""
if query_params:
    query_string = "?" + "&".join(query_params)

query_string_topn = query_string
if query_string:
    query_string_topn += f"&top_n={top_n}"
else:
    query_string_topn = f"?top_n={top_n}"


# ===============================
# LOAD FILTERED DATA
# ===============================
kpi_df = load_data("/kpi_filtered" + query_string)
month_df = load_data("/summary/month_filtered" + query_string)
country_df = load_data("/summary/country_filtered" + query_string_topn)
productline_df = load_data("/summary/productline_filtered" + query_string_topn)
sales_df = load_data("/sales_filtered" + query_string)


# ===============================
# KPI SECTION
# ===============================
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"${kpi_df['total_revenue'][0]:,.2f}")
col2.metric("🧾 Total Orders", int(kpi_df['total_orders'][0]))
col3.metric("📦 Avg Order Value", f"${kpi_df['avg_order_value'][0]:,.2f}")

st.markdown("---")


# ===============================
# ROW 1 — FILTERED COUNTRY + YEAR
# ===============================
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🌍 Top {top_n} Countries by Sales")
    st.bar_chart(
        country_df.set_index("country")["total_sales"]
    )

with col2:
    st.subheader("📅 Sales by Year")
    st.line_chart(
        year_df.set_index("year")["total_sales"]
    )


# ===============================
# ROW 2 — FILTERED PRODUCT LINE + DEAL SIZE
# ===============================
col3, col4 = st.columns(2)

with col3:
    st.subheader(f"🚗 Top {top_n} Product Lines by Sales")
    st.bar_chart(
        productline_df.set_index("productline")["total_sales"]
    )

with col4:
    st.subheader("📦 Sales by Deal Size")
    st.bar_chart(
        dealsize_df.set_index("dealsize")["total_sales"]
    )


# ===============================
# ROW 3 — STATUS + MONTH TREND
# ===============================
col5, col6 = st.columns(2)

with col5:
    st.subheader("📌 Sales by Status")
    st.bar_chart(
        status_df.set_index("status")["total_sales"]
    )

with col6:
    st.subheader("📈 Monthly Sales Trend")

    month_df["year_month"] = (
        month_df["year"].astype(str) + "-" +
        month_df["month"].astype(str).str.zfill(2)
    )

    trend_df = month_df.sort_values(["year", "month"])
    st.line_chart(
        trend_df.set_index("year_month")["total_sales"]
    )


# ===============================
# CSV EXPORT
# ===============================
st.markdown("---")
st.subheader("⬇️ Export Filtered Sales Data")

csv_data = sales_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)


# ===============================
# RAW DATA PREVIEW
# ===============================
st.subheader("📋 Filtered Sales Records")
st.dataframe(sales_df)
