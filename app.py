import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(page_title="Sales & Revenue Dashboard", page_icon="📊", layout="wide")

# Title
st.title("📊 Sales & Revenue Analysis Dashboard")
st.markdown("Interactive dashboard to analyze sales trends, top products, and regional performance.")

# Generate Dummy Data for Demonstration
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", end="2026-06-30", freq="D")
    data = {
        "Date": np.random.choice(dates, size=1500),
        "Product": np.random.choice(["Laptop", "Smartphone", "Headphones", "Smartwatch", "Tablet"], size=1500),
        "Region": np.random.choice(["North", "South", "East", "West"], size=1500),
        "Quantity": np.random.randint(1, 5, size=1500),
        "Price": np.random.choice([500, 800, 1200, 150, 300], size=1500)
    }
    df = pd.DataFrame(data)
    df["Revenue"] = df["Quantity"] * df["Price"]
    df["Cost"] = df["Revenue"] * 0.7  # Assuming 70% cost
    df["Profit"] = df["Revenue"] - df["Cost"]
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# Region Filter
regions = st.sidebar.multiselect("Select Region(s):", options=df["Region"].unique(), default=df["Region"].unique())

# Product Filter
products = st.sidebar.multiselect("Select Product(s):", options=df["Product"].unique(), default=df["Product"].unique())

# Filtered Data
filtered_df = df[(df["Region"].isin(regions)) & (df["Product"].isin(products))]

# Check if data exists after filtering
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # KPI Metrics Section
    total_revenue = filtered_df["Revenue"].sum()
    total_profit = filtered_df["Profit"].sum()
    total_units = filtered_df["Quantity"].sum()
    avg_order_value = filtered_df["Revenue"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Units Sold", f"{total_units:,}")
    col4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

    st.markdown("---")

    # Visualizations Section
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("📈 Monthly Revenue Trend")
        monthly_trend = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Revenue"].sum().reset_index()
        monthly_trend["Date"] = monthly_trend["Date"].astype(str)
        fig_trend = px.line(monthly_trend, x="Date", y="Revenue", markers=True, title="Revenue Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

    with row1_col2:
        st.subheader("🏆 Top Performing Products")
        top_products = filtered_df.groupby("Product")["Revenue"].sum().reset_index().sort_values(by="Revenue", ascending=True)
        fig_products = px.bar(top_products, x="Revenue", y="Product", orientation="h", title="Revenue by Product")
        st.plotly_chart(fig_products, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("🌍 Sales by Region")
        region_sales = filtered_df.groupby("Region")["Revenue"].sum().reset_index()
        fig_region = px.pie(region_sales, names="Region", values="Revenue", hole=0.4, title="Regional Revenue Share")
        st.plotly_chart(fig_region, use_container_width=True)

    with row2_col2:
        st.subheader("📋 Raw Data Preview")
        st.dataframe(filtered_df.head(100), use_container_width=True)