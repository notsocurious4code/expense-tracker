import streamlit as st
import pandas as pd
from database import (
    create_table,
    register_user,
    login_user,
    add_expense,
    get_expenses,
    delete_expense,
    update_expense
)

# Initialize DB
create_table()

# Session state
if "user" not in st.session_state:
    st.session_state.user = None

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


# =========================
# AUTH SECTION
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

    if choice == "Login":
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

    user_id = st.session_state.user[0]
    username = st.session_state.user[1]

    st.title("💰 Expense Tracker Dashboard")
    st.sidebar.write(f"Logged in as: {username}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # ---- Add Expense ----
    st.header("Add New Expense")

    date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
    )
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
        df = pd.DataFrame(
            expenses,
            columns=["ID", "Date", "Category", "Description", "Amount"]
        )

        # Display with Edit/Delete buttons
        for index, row in df.iterrows():

            col1, col2, col3 = st.columns([5, 1, 1])

            col1.write(
                f"{row['Date']} | {row['Category']} | {row['Description']} | ₹ {row['Amount']}"
            )

            if col2.button("Delete", key=f"delete_{row['ID']}"):
                delete_expense(row["ID"], user_id)
                st.success("Expense deleted.")
                st.rerun()

            if col3.button("Edit", key=f"edit_{row['ID']}"):
                st.session_state.edit_id = row["ID"]

        # ---- Edit Form ----
        if st.session_state.edit_id:

            edit_row = df[df["ID"] == st.session_state.edit_id].iloc[0]

            st.subheader("Edit Expense")

            new_date = st.date_input(
                "Edit Date",
                pd.to_datetime(edit_row["Date"])
            )

            categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]

            new_category = st.selectbox(
                "Edit Category",
                categories,
                index=categories.index(edit_row["Category"])
            )

            new_description = st.text_input(
                "Edit Description",
                value=edit_row["Description"]
            )

            new_amount = st.number_input(
                "Edit Amount",
                value=float(edit_row["Amount"]),
                min_value=0.0,
                format="%.2f"
            )

            col1, col2 = st.columns(2)

            if col1.button("Update Expense"):
                update_expense(
                    st.session_state.edit_id,
                    user_id,
                    str(new_date),
                    new_category,
                    new_description,
                    new_amount
                )
                st.success("Expense updated.")
                st.session_state.edit_id = None
                st.rerun()

            if col2.button("Cancel"):
                st.session_state.edit_id = None
                st.rerun()

        # ---- Summary ----
        total_spent = df["Amount"].sum()
        st.write(f"### Total Spent: ₹ {total_spent:.2f}")

        # ---- Budget ----
        st.subheader("Set Monthly Budget")
        budget = st.number_input("Enter your monthly budget", min_value=0.0, format="%.2f")

        if budget > 0:
            if total_spent > budget:
                st.error("⚠️ Budget Exceeded!")
            else:
                st.success("✅ You are within budget.")

        # ---- Charts ----
        category_summary = df.groupby("Category")["Amount"].sum()

        st.subheader("Spending by Category")
        st.bar_chart(category_summary)

        st.subheader("Category Distribution")
        st.pyplot(category_summary.plot.pie(autopct="%1.1f%%").figure)

        st.subheader("Monthly Spending Trend")
        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M")

        monthly_trend = df.groupby("Month")["Amount"].sum()
        st.line_chart(monthly_trend)

        # ---- Excel Export ----
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