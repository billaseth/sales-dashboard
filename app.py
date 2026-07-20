import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(page_title="Universal Data & Sales Analysis Dashboard", page_icon="📈", layout="wide")

st.title("📈 Universal Data & Sales Analysis Dashboard")
st.markdown("Upload any CSV or Excel file. The app will automatically map columns and analyze your data seamlessly without errors!")

# Sidebar File Uploader
st.sidebar.header("📁 Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

@st.cache_data
def get_sample_data():
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", end="2026-12-31", freq="D")
    df_sample = pd.DataFrame({
        "Date": np.random.choice(dates, size=500),
        "Category": np.random.choice(["Electronics", "Clothing", "Home", "Sports"], size=500),
        "Region": np.random.choice(["North", "South", "East", "West"], size=500),
        "Quantity": np.random.randint(1, 10, size=500),
        "Price": np.random.uniform(50, 500, size=500).round(2)
    })
    df_sample["Revenue"] = df_sample["Quantity"] * df_sample["Price"]
    return df_sample

# Load data safely
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheet_name = xls.sheet_names[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        df = get_sample_data()
else:
    df = get_sample_data()

# Clean column headers
df.columns = [str(col).strip() for col in df.columns]

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Smart Column Selection")

columns = list(df.columns)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
text_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

def find_best_match(keywords, cols):
    for col in cols:
        if any(kw in col.lower() for kw in keywords):
            return col
    return cols[0] if cols else None

default_val = find_best_match(["value", "revenue", "price", "amount", "sales", "total", "cost"], numeric_cols) if numeric_cols else (columns[0] if columns else None)
default_cat = find_best_match(["product", "name", "category", "rep", "item", "type"], text_cols) if text_cols else (columns[0] if columns else None)
default_loc = find_best_match(["region", "postcode", "city", "state", "location", "area"], text_cols) if text_cols else (columns[0] if columns else None)

val_col = st.sidebar.selectbox("Select Numeric/Value Column", options=numeric_cols if numeric_cols else columns, index=numeric_cols.index(default_val) if default_val in numeric_cols else 0, key="val_col_select")
cat_col = st.sidebar.selectbox("Select Category Column", options=columns, index=columns.index(default_cat) if default_cat in columns else 0, key="cat_col_select")
loc_col = st.sidebar.selectbox("Select Grouping Column", options=columns, index=columns.index(default_loc) if default_loc in columns else 0, key="loc_col_select")

# Preprocessing data safely
try:
    df["_Analysis_Value_"] = pd.to_numeric(df[val_col], errors='coerce').fillna(0)
except Exception:
    df["_Analysis_Value_"] = 0

# Sidebar Dynamic Filters with Unique Keys
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

unique_cats = df[cat_col].dropna().unique().tolist()
selected_cats = st.sidebar.multiselect(f"Filter {cat_col}:", options=unique_cats, default=unique_cats, key="cat_multiselect_filter")

unique_locs = df[loc_col].dropna().unique().tolist()
selected_locs = st.sidebar.multiselect(f"Filter {loc_col}:", options=unique_locs, default=unique_locs, key="loc_multiselect_filter")

filtered_df = df[df[cat_col].isin(selected_cats) & df[loc_col].isin(selected_locs)]

if filtered_df.empty:
    st.warning("No data found for the selected filter combination.")
else:
    total_val = filtered_df["_Analysis_Value_"].sum()
    mean_val = filtered_df["_Analysis_Value_"].mean()
    record_count = len(filtered_df)
    max_val = filtered_df["_Analysis_Value_"].max()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Value", f"{total_val:,.2f}")
    c2.metric("Average Value", f"{mean_val:,.2f}")
    c3.metric("Total Records", f"{record_count:,}")
    c4.metric("Maximum Value", f"{max_val:,.2f}")

    st.markdown("---")

    r1_c1, r1_c2 = st.columns(2)

    with r1_c1:
        st.subheader(f"📊 Distribution by {cat_col}")
        cat_group = filtered_df.groupby(cat_col)["_Analysis_Value_"].sum().reset_index().sort_values(by="_Analysis_Value_", ascending=True)
        fig_cat = px.bar(cat_group, x="_Analysis_Value_", y=cat_col, orientation="h", title=f"Total Value per {cat_col}")
        st.plotly_chart(fig_cat, use_container_width=True)

    with r1_c2:
        st.subheader(f"🌍 Share by {loc_col}")
        loc_group = filtered_df.groupby(loc_col)["_Analysis_Value_"].sum().reset_index()
        fig_loc = px.pie(loc_group, names=loc_col, values="_Analysis_Value_", hole=0.4, title=f"Proportion by {loc_col}")
        st.plotly_chart(fig_loc, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Raw Data & Processed View")
    st.dataframe(filtered_df.head(200), use_container_width=True)