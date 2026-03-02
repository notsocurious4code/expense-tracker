import streamlit as st
import pandas as pd
from database import (
    create_table,
    register_user,
    login_user,
    add_expense,
    get_expenses
)

# Initialize database
create_table()

# Session state
if "user" not in st.session_state:
    st.session_state.user = None


# =========================
# AUTHENTICATION SECTION
# =========================

if st.session_state.user is None:

    st.title("🔐 Expense Tracker")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            if username and password:
                if register_user(username, password):
                    st.success("User registered successfully!")
                else:
                    st.error("Username already exists.")
            else:
                st.warning("Please fill all fields.")

    elif choice == "Login":
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")


# =========================
# DASHBOARD SECTION
# =========================

else:

    st.title("💰 Expense Tracker Dashboard")

    st.sidebar.write(f"Logged in as: {st.session_state.user[1]}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    user_id = st.session_state.user[0]

    # ---- Add Expense ----
    st.header("Add New Expense")

    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    if st.button("Add Expense"):
        add_expense(user_id, str(date), category, description, amount)
        st.success("Expense Added Successfully!")
        st.rerun()

    # ---- View Expenses ----
    st.header("All Expenses")

    expenses = get_expenses(user_id)

    if expenses:
        df = pd.DataFrame(expenses, columns=["ID", "Date", "Category", "Description", "Amount"])
        st.dataframe(df)

        # Summary
        total_spent = df["Amount"].sum()
        st.write(f"### Total Spent: ₹ {total_spent:.2f}")

        # Budget
        st.subheader("Set Monthly Budget")
        budget = st.number_input("Enter your monthly budget", min_value=0.0, format="%.2f")

        if budget > 0:
            if total_spent > budget:
                st.error("⚠️ Budget Exceeded!")
            else:
                st.success("✅ You are within budget.")

        # Category-wise Spending
        category_summary = df.groupby("Category")["Amount"].sum()

        st.subheader("Spending by Category")
        st.bar_chart(category_summary)

        st.subheader("Category Distribution")
        st.pyplot(category_summary.plot.pie(autopct="%1.1f%%").figure)

        # Monthly Trend
        st.subheader("Monthly Spending Trend")
        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M")

        monthly_trend = df.groupby("Month")["Amount"].sum()
        st.line_chart(monthly_trend)

        # Export to Excel
        st.subheader("Export Report")

        if st.button("Generate Excel Report"):
            excel_file = "expense_report.xlsx"
            df.to_excel(excel_file, index=False)

            with open(excel_file, "rb") as f:
                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name="expense_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    else:
        st.info("No expenses added yet.")