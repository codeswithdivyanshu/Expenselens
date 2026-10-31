
# ExpenseLens
# Personal Expense Analysis & Visualization Dashboard

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Page configuration
st.set_page_config(
    page_title="ExpenseLens",
    page_icon="💰",
    layout="wide"
)

# Project title
st.title("ExpenseLens")
st.subheader("Personal Expense Analysis Dashboard")

# CSV file location
FILE = os.path.join(os.path.dirname(__file__), "expenses.csv")

# Load expense data
def load_expenses():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)

    return pd.DataFrame(
        columns=["Date", "Name", "Category", "Amount"]
    )

# Save expense data
def save_expenses(data):
    data.to_csv(FILE, index=False)

# Read existing data
df = load_expenses()

# Expense entry form
st.header("Add New Expense")

with st.form("expense_form"):

    date = st.date_input("Expense Date")

    name = st.text_input("Expense Name")

    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Education", "Other"]
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=10.0
    )

    submit = st.form_submit_button("Add Expense")

    if submit:
        if name.strip() and amount > 0:

            new_expense = pd.DataFrame([{
                "Date": str(date),
                "Name": name,
                "Category": category,
                "Amount": amount
            }])

            df = pd.concat(
                [df, new_expense],
                ignore_index=True
            )

            save_expenses(df)

            st.success("Expense added successfully!")

            st.rerun()

        else:
            st.warning("Enter a valid name and amount.")
            # Clear / Reset Data Button in Sidebar
    if st.sidebar.button("Clear All Data"):
        import os
        if os.path.exists(FILE):
            os.remove(FILE)
        
        if 'df' in st.session_state:
            del st.session_state['df']
            
        st.cache_data.clear()
        st.success("saara data clear ho jata h!!")
        st.rerun()

# Display expense analysis
st.header("Expense Summary")

if not df.empty:

    total = df["Amount"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Expenses", f"₹{total:,.2f}")

    col2.metric("Total Entries", len(df))

    # Highest Spending Category Calculation
if not df.empty and "Category" in df.columns and "Amount" in df.columns:
    category_totals = df.groupby("Category")["Amount"].sum()
    if not category_totals.empty:
        highest_category = category_totals.idxmax()
        highest_amount = category_totals.max()
        col3.metric("Highest Spending", f"{highest_category} (₹{highest_amount:,.2f})")

    st.subheader("All Expenses")
    st.dataframe(df, use_container_width=True)

    # Category analysis
    category_data = df.groupby("Category")["Amount"].sum()

    # Pie chart
    st.subheader("Category-wise Pie Chart")

    fig1, ax1 = plt.subplots(figsize=(4,3))

    ax1.pie(
        category_data,
        labels=category_data.index,
        autopct="%1.1f%%"
    )

    ax1.set_title("Expense Distribution")

    st.pyplot(fig1, use_container_width=False)
    plt.close(fig1)

    # Bar graph
    st.subheader("Category-wise Bar Graph")

    fig2, ax2 = plt.subplots(figsize=(4,3))

    ax2.bar(
        category_data.index,
        category_data.values
    )

    ax2.set_title("Expense Comparison")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Amount (₹)")

    st.pyplot(fig2, use_container_width=False)
    plt.close(fig2)

    # Monthly Expense Line Chart

    st.subheader("Monthly Expense Trend")

    # Convert Date column into datetime format
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Remove invalid dates
    monthly_data = df.dropna(subset=["Date"]).copy()

    # Extract month from date
    monthly_data["Month"] = (
        monthly_data["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Monthly & Date-wise Expense Trend Analysis
    if not df.empty and "Date" in df.columns:
        # Date column ko datetime format mein convert karna
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Date ko readable format mein banana (jaise "31 Oct 2026")
        df["Formatted_Date"] = df["Date"].dt.strftime("%d %b %Y")
        
        # Line chart ke liye date-wise data group karna
        trend_data = df.groupby("Date")["Amount"].sum().reset_index()
        
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        import matplotlib.dates as mdates
        from matplotlib.dates import DayLocator
        
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        
        # har date sirf ek hi baar aaye, iske liye 1 day ka gap set karna
        ax3.xaxis.set_major_locator(DayLocator(interval=1))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
        ax3.plot(
            trend_data["Date"], 
            trend_data["Amount"], 
            marker="o", 
            color="#ff4b4b", 
            linewidth=2
        )
        
        ax3.set_title("Date-wise Expense Trend", fontsize=14, fontweight='bold')
        ax3.set_xlabel("Date (Day-wise)", fontsize=11)
        ax3.set_ylabel("Amount (₹)", fontsize=11)
        
        # Axis ko sirf available dates ke hisab se zoom/adjust karna
        ax3.set_xlim(trend_data["Date"].min() - pd.Timedelta(days=2), trend_data["Date"].max() + pd.Timedelta(days=2))
        
        # Dates ko rotate karna taaki overlap na ho
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig3, use_container_width=False)
        plt.close(fig3)
else:
    st.info("No expenses yet. Add your first expense!")


    