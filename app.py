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

# ---------------------------
# Initial Setup
# ---------------------------

st.set_page_config(page_title="Expense Tracker", layout="wide")
create_table()

if "user" not in st.session_state:
    st.session_state.user = None

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


# =========================
# AUTH SECTION
# =========================

if st.session_state.user is None:

    st.title("Expense Tracker")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            if username and password:
                if register_user(username, password):
                    st.success("User registered successfully.")
                else:
                    st.error("Username already exists.")
            else:
                st.warning("Fill all fields.")

    if choice == "Login":
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid credentials.")


# =========================
# DASHBOARD
# =========================

else:

    user_id = st.session_state.user[0]
    username = st.session_state.user[1]

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Expense", "Reports"])

    st.sidebar.markdown("---")
    st.sidebar.write(f"User: {username}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    expenses = get_expenses(user_id)
    df = pd.DataFrame(
        expenses,
        columns=["ID", "Date", "Category", "Description", "Amount"]
    ) if expenses else pd.DataFrame(columns=["ID", "Date", "Category", "Description", "Amount"])


    # ================= DASHBOARD PAGE =================

    if page == "Dashboard":

        st.title("Financial Overview")

        if not df.empty:

            total_spent = df["Amount"].sum()
            expense_count = len(df)

            col1, col2 = st.columns(2)

            col1.metric("Total Spent", f"₹ {total_spent:.2f}")
            col2.metric("Total Transactions", expense_count)

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Spending by Category")
                category_summary = df.groupby("Category")["Amount"].sum()
                st.bar_chart(category_summary)

            with col2:
                st.subheader("Category Distribution")
                st.pyplot(category_summary.plot.pie(autopct="%1.1f%%").figure)

            st.markdown("---")

            st.subheader("Monthly Trend")
            df["Date"] = pd.to_datetime(df["Date"])
            df["Month"] = df["Date"].dt.to_period("M")
            monthly_trend = df.groupby("Month")["Amount"].sum()
            st.line_chart(monthly_trend)

        else:
            st.info("No expenses recorded yet.")


    # ================= ADD EXPENSE PAGE =================

    if page == "Add Expense":

        st.title("Add New Expense")

        date = st.date_input("Date")
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        )
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")

        if st.button("Add Expense"):
            add_expense(user_id, str(date), category, description, amount)
            st.success("Expense added successfully.")
            st.rerun()


    # ================= REPORTS PAGE =================

    if page == "Reports":

        st.title("Expense Management")

        if not df.empty:

            # CRUD display
            for index, row in df.iterrows():

                col1, col2, col3 = st.columns([6, 1, 1])

                col1.write(
                    f"{row['Date']} | {row['Category']} | {row['Description']} | ₹ {row['Amount']}"
                )

                if col2.button("Delete", key=f"delete_{row['ID']}"):
                    delete_expense(row["ID"], user_id)
                    st.rerun()

                if col3.button("Edit", key=f"edit_{row['ID']}"):
                    st.session_state.edit_id = row["ID"]

            # Edit Section
            if st.session_state.edit_id:

                edit_row = df[df["ID"] == st.session_state.edit_id].iloc[0]

                st.markdown("---")
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
                    st.session_state.edit_id = None
                    st.rerun()

                if col2.button("Cancel"):
                    st.session_state.edit_id = None
                    st.rerun()

            st.markdown("---")

            # Export
            st.subheader("Export Data")

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
            st.info("No expenses available.")