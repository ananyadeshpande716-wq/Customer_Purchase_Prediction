
"""Customer Purchase Prediction application — Streamlit frontend."""

import pandas as pd
import streamlit as st
from pymongo.errors import PyMongoError

from src.mongodb import check_connection, get_database
from src.customer_service import (
    create_customer,
    delete_customer,
    list_customers,
    search_customers,
    update_customer,
)


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Customer Purchase Prediction",
    page_icon="🛍️",
    layout="wide",
)

st.title("🛍️ Customer Purchase Prediction")
st.caption(
    "Customer management and purchase analytics "
    "powered by MongoDB and machine learning."
)


# --------------------------------------------------
# Database connection
# --------------------------------------------------

try:
    check_connection()
    db = get_database()

except Exception as exc:
    st.error(
        "Could not connect to MongoDB Atlas. "
        "Check your .env file, Atlas network access, "
        "and active Python environment."
    )
    st.caption(f"Error type: {type(exc).__name__}")
    st.stop()


# --------------------------------------------------
# Sidebar navigation
# --------------------------------------------------

st.sidebar.title("Navigation")
st.sidebar.success("MongoDB connected")

page = st.sidebar.radio(
    "Choose a page",
    ["Dashboard", "Customer Management"],
)

st.sidebar.divider()
st.sidebar.caption("Customer Purchase Prediction System")


# --------------------------------------------------
# Dashboard
# --------------------------------------------------

if page == "Dashboard":

    st.subheader("Project Dashboard")
    st.write(
        "Overview of registered customer profiles, "
        "historical feature records, and saved predictions."
    )

    try:
        customer_count = db["customers"].count_documents({})
        feature_count = db["customer_features"].count_documents({})
        prediction_count = db["prediction_history"].count_documents({})

        positive_count = db["prediction_history"].count_documents(
            {"predicted_purchase": 1}
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Registered Customers", customer_count)
        col2.metric("Feature Records", feature_count)
        col3.metric("Saved Predictions", prediction_count)
        col4.metric("Predicted Purchases", positive_count)

        st.divider()
        st.subheader("Recently Updated Customer Profiles")

        recent_customers = list_customers(limit=10)

        if recent_customers:
            st.dataframe(
                pd.DataFrame(recent_customers),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No customer profiles have been registered yet. "
                "Open Customer Management to add your first customer."
            )

    except PyMongoError as exc:
        st.error(f"Could not retrieve dashboard data: {type(exc).__name__}")


# --------------------------------------------------
# Customer Management
# --------------------------------------------------

elif page == "Customer Management":

    st.subheader("Customer Management")
    st.write(
        "Create, search, update, and delete customer profiles. "
        "Changes are saved directly to MongoDB Atlas."
    )

    add_tab, search_tab, update_tab, delete_tab = st.tabs(
        [
            "➕ Add Customer",
            "🔎 Search / View",
            "✏️ Update Customer",
            "🗑️ Delete Customer",
        ]
    )

    # ----------------------------------------------
    # CREATE
    # ----------------------------------------------

    with add_tab:

        st.markdown("#### Register a Customer")

        with st.form("create_customer_form", clear_on_submit=True):

            new_id = st.text_input(
                "Customer ID *",
                max_chars=50,
                help="Enter a unique customer ID.",
            )

            new_name = st.text_input(
                "Customer Name *",
                max_chars=100,
            )

            new_country = st.text_input(
                "Country *",
                max_chars=100,
            )

            new_notes = st.text_area(
                "Notes (optional)",
                max_chars=500,
            )

            create_submitted = st.form_submit_button(
                "Add Customer",
                type="primary",
            )

        if create_submitted:
            try:
                document_id = create_customer(
                    customer_id=new_id,
                    customer_name=new_name,
                    country=new_country,
                    notes=new_notes,
                )

                st.success(
                    f"Customer registered successfully. "
                    f"Database record ID: {document_id}"
                )
                st.rerun()

            except ValueError as exc:
                st.error(str(exc))

            except PyMongoError as exc:
                st.error(
                    f"Database operation failed: {type(exc).__name__}"
                )

    # ----------------------------------------------
    # READ / SEARCH
    # ----------------------------------------------

    with search_tab:

        st.markdown("#### Search Customer Profiles")
        st.caption(
            "Search by customer ID or name. "
            "Country filtering is optional."
        )

        with st.form("search_customer_form"):

            search_text = st.text_input(
                "Customer ID or name",
                max_chars=100,
            )

            country_filter = st.text_input(
                "Filter by country",
                max_chars=100,
            )

            page_number = st.number_input(
                "Page number",
                min_value=1,
                value=1,
                step=1,
            )

            page_size = st.selectbox(
                "Records per page",
                [10, 20, 50, 100],
                index=1,
            )

            search_submitted = st.form_submit_button(
                "Search Customers",
                type="primary",
            )

        if search_submitted:
            try:
                result = search_customers(
                    search_text=search_text,
                    country=country_filter or None,
                    page=int(page_number),
                    page_size=page_size,
                )

                # Keep results across Streamlit reruns.
                st.session_state["customer_search_result"] = result

            except ValueError as exc:
                st.error(str(exc))

            except PyMongoError as exc:
                st.error(
                    f"Search failed: {type(exc).__name__}"
                )

        result = st.session_state.get("customer_search_result")

        if result is not None:
            st.caption(
                f"Matching records: {result['total']} | "
                f"Page {result['page']} of {result['total_pages']}"
            )

            if result["items"]:
                st.dataframe(
                    pd.DataFrame(result["items"]),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No matching customer records found.")

    # ----------------------------------------------
    # UPDATE
    # ----------------------------------------------

    with update_tab:

        st.markdown("#### Update Customer Details")
        st.caption(
            "Enter the customer ID. Leave optional update fields "
            "blank to preserve their existing values."
        )

        with st.form("update_customer_form"):

            update_id = st.text_input(
                "Customer ID *",
                max_chars=50,
                key="update_customer_id",
            )

            update_name = st.text_input(
                "New customer name (optional)",
                max_chars=100,
            )

            update_country = st.text_input(
                "New country (optional)",
                max_chars=100,
            )

            update_notes = st.text_area(
                "New notes (optional)",
                max_chars=500,
            )

            update_submitted = st.form_submit_button(
                "Update Customer",
                type="primary",
            )

        if update_submitted:
            try:
                changed = update_customer(
                    customer_id=update_id,
                    customer_name=update_name or None,
                    country=update_country or None,
                    notes=update_notes or None,
                )

                if changed:
                    st.success("Customer updated successfully.")
                    st.rerun()
                else:
                    st.warning(
                        "No customer profile with that ID was found."
                    )

            except ValueError as exc:
                st.error(str(exc))

            except PyMongoError as exc:
                st.error(
                    f"Update failed: {type(exc).__name__}"
                )

    # ----------------------------------------------
    # DELETE
    # ----------------------------------------------

    with delete_tab:

        st.markdown("#### Delete a Customer Profile")

        st.warning(
            "This permanently deletes the selected document "
            "from the customers collection. It does not delete "
            "the historical ML features or prediction history."
        )

        with st.form("delete_customer_form"):

            delete_id = st.text_input(
                "Customer ID *",
                max_chars=50,
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this customer profile."
            )

            delete_submitted = st.form_submit_button(
                "Delete Customer",
                type="primary",
            )

        if delete_submitted:

            if not confirm_delete:
                st.warning(
                    "Please confirm the deletion before continuing."
                )

            else:
                try:
                    deleted = delete_customer(delete_id)

                    if deleted:
                        st.success("Customer profile deleted successfully.")
                        st.rerun()
                    else:
                        st.warning(
                            "No customer profile with that ID was found."
                        )

                except ValueError as exc:
                    st.error(str(exc))

                except PyMongoError as exc:
                    st.error(
                        f"Delete failed: {type(exc).__name__}"
                    )
