import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

[data-testid="stSidebar"] {
    background-color: #161b22;
}

.dashboard-title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

.metric-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}

.metric-title {
    color: #9ca3af;
    font-size: 14px;
}

.metric-value {
    font-size: 25px;
    font-weight: bold;
    margin-top: 8px;
}

.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 25px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="dashboard-title">📊 Sales Data Analysis Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Interactive Sales Data Analysis using Python'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# LOAD CSV
# ==========================================

try:
    df = pd.read_csv("sales_data.csv")

except FileNotFoundError:
    st.error("❌ sales_data.csv file not found.")
    st.info(
        "Make sure sales_data.csv is in the same folder as app.py."
    )
    st.stop()

except Exception as e:
    st.error("❌ Error while reading sales_data.csv")
    st.write(e)
    st.stop()

# ==========================================
# UPLOAD CSV
# ==========================================

st.sidebar.title("📂 Data Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload another CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

    except Exception as e:
        st.sidebar.error("Unable to read uploaded CSV.")
        st.write(e)
        st.stop()

# ==========================================
# REQUIRED COLUMNS
# ==========================================

required_columns = [
    "Date",
    "Product",
    "Category",
    "Region",
    "Quantity",
    "Sales"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "❌ Missing columns: "
        + ", ".join(missing_columns)
    )

    st.info(
        "Required columns: Date, Product, Category, "
        "Region, Quantity, Sales"
    )

    st.stop()

# ==========================================
# DATA CLEANING
# ==========================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
)

df["Sales"] = pd.to_numeric(
    df["Sales"],
    errors="coerce"
)

df["Quantity"] = df["Quantity"].fillna(0)
df["Sales"] = df["Sales"].fillna(0)

df = df.dropna(subset=["Date"])

# Remove completely empty rows

df = df.dropna(
    how="all"
)

if df.empty:
    st.error("❌ No valid data available.")
    st.stop()

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Filters")

# Date filter

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Category filter

categories = sorted(
    df["Category"].dropna().astype(str).unique()
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)

# Region filter

regions = sorted(
    df["Region"].dropna().astype(str).unique()
)

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

# Product filter

products = sorted(
    df["Product"].dropna().astype(str).unique()
)

selected_products = st.sidebar.multiselect(
    "Product",
    products,
    default=products
)

# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df.copy()

if len(date_range) == 2:

    start_date = pd.to_datetime(
        date_range[0]
    )

    end_date = pd.to_datetime(
        date_range[1]
    )

    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        &
        (filtered_df["Date"] <= end_date)
    ]

filtered_df = filtered_df[
    filtered_df["Category"].astype(str).isin(
        selected_categories
    )
]

filtered_df = filtered_df[
    filtered_df["Region"].astype(str).isin(
        selected_regions
    )
]

filtered_df = filtered_df[
    filtered_df["Product"].astype(str).isin(
        selected_products
    )
]

# ==========================================
# EMPTY FILTER CHECK
# ==========================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data found for the selected filters."
    )

    st.stop()

# ==========================================
# KPI CALCULATIONS
# ==========================================

total_sales = filtered_df["Sales"].sum()

total_orders = len(filtered_df)

total_quantity = filtered_df["Quantity"].sum()

total_products = filtered_df["Product"].nunique()

average_sales = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

# ==========================================
# KPI SECTION
# ==========================================

st.markdown(
    '<div class="section-title">'
    '📌 Key Performance Indicators'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Total Sales
            </div>
            <div class="metric-value">
                ₹{total_sales:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Total Orders
            </div>
            <div class="metric-value">
                {total_orders:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Quantity Sold
            </div>
            <div class="metric-value">
                {total_quantity:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Products
            </div>
            <div class="metric-value">
                {total_products}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                Average Sale
            </div>
            <div class="metric-value">
                ₹{average_sales:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# MONTHLY SALES
# ==========================================

st.markdown(
    '<div class="section-title">'
    '📈 Monthly Sales Trend'
    '</div>',
    unsafe_allow_html=True
)

monthly_sales = (
    filtered_df
    .groupby(
        filtered_df["Date"].dt.to_period("M")
    )["Sales"]
    .sum()
    .reset_index()
)

monthly_sales["Date"] = (
    monthly_sales["Date"]
    .astype(str)
)

fig_monthly = px.line(
    monthly_sales,
    x="Date",
    y="Sales",
    markers=True,
    title="Monthly Sales"
)

fig_monthly.update_layout(
    template="plotly_dark",
    xaxis_title="Month",
    yaxis_title="Sales (₹)"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# ==========================================
# CATEGORY SALES
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        '<div class="section-title">'
        '📊 Category-wise Sales'
        '</div>',
        unsafe_allow_html=True
    )

    category_sales = (
        filtered_df
        .groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        title="Sales by Category"
    )

    fig_category.update_layout(
        template="plotly_dark",
        xaxis_title="Category",
        yaxis_title="Sales (₹)"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

# ==========================================
# REGION SALES
# ==========================================

with col2:

    st.markdown(
        '<div class="section-title">'
        '🌍 Region-wise Sales'
        '</div>',
        unsafe_allow_html=True
    )

    region_sales = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .reset_index()
    )

    fig_region = px.pie(
        region_sales,
        names="Region",
        values="Sales",
        title="Sales Distribution by Region",
        hole=0.4
    )

    fig_region.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

# ==========================================
# TOP PRODUCTS
# ==========================================

st.markdown(
    '<div class="section-title">'
    '🏆 Top Products'
    '</div>',
    unsafe_allow_html=True
)

top_products = (
    filtered_df
    .groupby("Product")["Sales"]
    .sum()
    .reset_index()
    .sort_values(
        "Sales",
        ascending=False
    )
    .head(10)
)

fig_products = px.bar(
    top_products,
    x="Sales",
    y="Product",
    orientation="h",
    title="Top 10 Products"
)

fig_products.update_layout(
    template="plotly_dark",
    xaxis_title="Sales (₹)",
    yaxis_title="Product"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)

# ==========================================
# DATA TABLE
# ==========================================

st.markdown(
    '<div class="section-title">'
    '📋 Sales Data'
    '</div>',
    unsafe_allow_html=True
)

display_df = filtered_df.copy()

display_df["Date"] = display_df[
    "Date"
].dt.strftime("%d-%m-%Y")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# DOWNLOAD
# ==========================================

st.markdown(
    '<div class="section-title">'
    '📥 Download Data'
    '</div>',
    unsafe_allow_html=True
)

download_df = filtered_df.copy()

csv_data = download_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#9ca3af;
        padding:15px;
    ">
        📊 Sales Data Analysis Dashboard<br>
        Built with Python • Pandas • Plotly • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
