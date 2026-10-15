import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Supply Chain Analytics Dashboard")
st.subheader(
    "Customer, Product, and Profitability Performance Analysis"
)

st.write(
    "Upload APL_Logistics.csv to analyze sales, profit, "
    "customer segments, product categories, and discounts."
)

uploaded_file = st.sidebar.file_uploader(
    "Upload APL_Logistics.csv",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Upload your CSV dataset using the sidebar to begin.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file, encoding="latin1")
except Exception as error:
    st.error(f"Unable to read the dataset: {error}")
    st.stop()

st.success("Dataset loaded successfully!")

required_columns = [
    "Sales",
    "Order Item Total",
    "Order Profit Per Order",
    "Order Item Discount Rate"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

for column in required_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

st.sidebar.header("Filters")

filtered_df = df.copy()

if "Customer Segment" in df.columns:
    segments = sorted(
        df["Customer Segment"].dropna().unique().tolist()
    )

    selected_segments = st.sidebar.multiselect(
        "Customer Segment",
        segments,
        default=segments
    )

    filtered_df = filtered_df[
        filtered_df["Customer Segment"].isin(selected_segments)
    ]

if "Market" in df.columns:
    markets = sorted(
        filtered_df["Market"].dropna().unique().tolist()
    )

    selected_markets = st.sidebar.multiselect(
        "Market",
        markets,
        default=markets
    )

    filtered_df = filtered_df[
        filtered_df["Market"].isin(selected_markets)
    ]

gross_sales = filtered_df["Sales"].sum()
net_sales = filtered_df["Order Item Total"].sum()
total_profit = filtered_df["Order Profit Per Order"].sum()

profit_margin = (
    total_profit / net_sales * 100
    if net_sales != 0 else 0
)

average_discount = (
    filtered_df["Order Item Discount Rate"].mean() * 100
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Gross Sales", f"{gross_sales:,.2f}")
col2.metric("Net Sales", f"{net_sales:,.2f}")
col3.metric("Recorded Profit", f"{total_profit:,.2f}")
col4.metric("Aggregate Profit Margin", f"{profit_margin:.2f}%")

st.metric("Average Discount Rate", f"{average_discount:.2f}%")

overview, products, customers, discounts = st.tabs([
    "Overview",
    "Product Analysis",
    "Customer Analysis",
    "Discount Analysis"
])

with overview:
    st.header("Dataset Overview")
    st.write("Rows:", len(filtered_df))
    st.write("Columns:", len(filtered_df.columns))

    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.head(100), use_container_width=True)

    st.subheader("Missing Values")
    st.dataframe(
        filtered_df.isnull().sum().to_frame("Missing Values"),
        use_container_width=True
    )

with products:
    st.header("Product Category Analysis")

    if "Category Name" in filtered_df.columns:
        category_analysis = filtered_df.groupby(
            "Category Name"
        ).agg(
            Total_Sales=("Order Item Total", "sum"),
            Total_Profit=("Order Profit Per Order", "sum")
        ).sort_values("Total_Sales", ascending=False)

        st.dataframe(category_analysis, use_container_width=True)

        st.bar_chart(category_analysis["Total_Sales"].head(10))
    else:
        st.warning("The Category Name column was not found.")

with customers:
    st.header("Customer Segment Analysis")

    if "Customer Segment" in filtered_df.columns:
        customer_analysis = filtered_df.groupby(
            "Customer Segment"
        ).agg(
            Total_Sales=("Order Item Total", "sum"),
            Total_Profit=("Order Profit Per Order", "sum")
        ).sort_values("Total_Profit", ascending=False)

        st.dataframe(customer_analysis, use_container_width=True)
        st.bar_chart(customer_analysis["Total_Profit"])
    else:
        st.warning("The Customer Segment column was not found.")

with discounts:
    st.header("Discount Analysis")

    discount_df = filtered_df.copy()

    discount_df["Discount Band"] = pd.cut(
        discount_df["Order Item Discount Rate"],
        bins=[-0.001, 0.05, 0.10, 0.20, 1.0],
        labels=["0–5%", "5–10%", "10–20%", "Above 20%"]
    )

    discount_analysis = discount_df.groupby(
        "Discount Band",
        observed=False
    ).agg(
        Items=("Order Item Discount Rate", "count"),
        Total_Sales=("Order Item Total", "sum"),
        Total_Profit=("Order Profit Per Order", "sum")
    )

    st.dataframe(discount_analysis, use_container_width=True)
    st.bar_chart(discount_analysis[["Total_Sales", "Total_Profit"]])

st.download_button(
    "Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_supply_chain_data.csv",
    mime="text/csv"
)

st.caption(
    "Note: Aggregate profit margin is calculated as recorded profit "
    "divided by net sales. Verify metric definitions before reporting."
)
