import streamlit as st
import pandas as pd
import numpy as np
from app.data.db import connect_database
# from app.services.user_service import load_csv_to_table
# from app.data.incidents import *
# from app.data.tickets import *
# from app.data.datasets import *
from my_app.services.database_manager import DatabaseManager
from my_app.models.security_incident import SecurityIncident
from my_app.models.dataset import Dataset
from my_app.models.it_ticket import ITTicket

st.set_page_config(page_title="Dashboard", page_icon="📊 ",
layout="wide")

# st.write("DEBUG:", st.session_state)

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
    st.stop()

# Setup database
conn = connect_database()

# If logged in, show dashboard content
st.title("📊 Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

# Example dashboard layout
st.caption("Welcome to the Multi-Domain Intelligence Platform")

# Allow category selections
categories = ["NONE", "Cybersecurity", "Data Science", "IT Operations"]

# Bind selectbox to session_state
with st.sidebar:
    selected_categories = st.selectbox(
        "Select a domain:",
        categories,
        index=categories.index(st.session_state.selected_categories),
        key="selected_categories"
    )
st.write("Selected domain: ", st.session_state.selected_categories)

if st.session_state.selected_categories == "NONE":
    # Shows no data
    # Logout button
    with st.sidebar:
        st.divider()
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.info("You have been logged out.")
            st.switch_page("Home.py")
    st.stop()

# ---------- Cybersecurity Display ----------
elif st.session_state.selected_categories == "Cybersecurity":

    db = DatabaseManager("app/data/DATA/intelligence_platform.db")
    db.connect()

    st.subheader("Cyber Incidents by Category (Monthly):")

    col1, col2 = st.columns(2)
    # Group incidents by month and category
    chart_data = """
           SELECT strftime('%Y-%m', timestamp) as month, category, COUNT(*) as count
           FROM cyber_incidents
           GROUP BY month, category
           ORDER BY month
           """
    # Connects to database to run chart_data and to make a dataframe
    df = pd.read_sql_query(chart_data, conn)

    df_pivot = df.pivot(index="month", columns="category", values="count").fillna(0)

    # Show bar chart
    with col1:
        st.subheader("Line chart")
        st.line_chart(df_pivot)


    # Show the line chart
    with col2:
        st.subheader("\nBar chart")
        st.bar_chart(df_pivot)

    rows = db.fetch_all(
        "SELECT incident_id, timestamp, severity, category, status, description, reported_by FROM cyber_incidents ORDER BY incident_id")

    incidents: list[SecurityIncident] = []
    for row in rows:
        incident = SecurityIncident(
            db_path= "app/data/DATA/intelligence_platform.db",
            incident_id=row[0],
            timestamp=row[1],
            incident_type=row[3],
            severity=row[2],
            status=row[4],
            description=row[5],
            reported_by=row[6],
        )
        incidents.append(incident)

    # Create DataFrame with named columns
    columns = ["incident_id", "timestamp", "severity", "category", "status", "description", "reported_by"]
    df = pd.DataFrame(rows, columns=columns)

    # Show DataFrame
    with st.expander("See raw data"):
        st.dataframe(df)

    # Allow category selections
    edit_categories = ["Add", "Remove", "Update Status"]
    selected_categories = st.selectbox("Edit Cyber Incidents:", edit_categories)

    # Insert new incident
    if selected_categories == "Add":
        st.subheader("Add New Incident")
        with st.form("insert_form"):
            timestamp = st.text_input("Timestamp (YYYY-MM-DD HH:MM:SS)")
            severity = st.selectbox("Severity", ["Low", "Medium", "High"])
            category = st.selectbox("Category", ["DDos", "Malware", "Misconfiguration", "Phishing", "Unauthorized Access"])
            status = st.selectbox("Status", ["Open", "Investigating", "Closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Insert Incident")

            if submitted:
                incident = SecurityIncident(
                    db_path= "app/data/DATA/intelligence_platform.db",
                    incident_id=None,
                    timestamp=timestamp,
                    severity=severity,
                    incident_type=category,
                    status=status,
                    description=description,
                    reported_by=reported_by,
                )

                incident_id = incident.save_changes("add")
                st.success(f"Incident {incident_id} inserted successfully!")
                st.rerun()

    # Remove incident
    elif selected_categories == "Remove":
        # Ensure state keys exist
        if "confirm_remove" not in st.session_state:
            st.session_state.confirm_remove = False
        if "incident_to_remove" not in st.session_state:
            st.session_state.incident_to_remove = ""

        st.subheader("Remove Incident")

        with st.form("remove_form"):
            incident_id = st.text_input("Incident ID")
            check_id = st.form_submit_button("Check Incident ID")
            # Check if the incident is in the database
            if check_id:
                self = SecurityIncident.get_self(incidents, int(incident_id))
                if self is None:
                    st.error("Error: Invalid Incident ID.")
                else:
                    st.write(incidents[self])

            submitted = st.form_submit_button("Remove Incident")

            if submitted:
                # Move into confirmation mode and remember the ID
                st.session_state.confirm_remove = True
                st.session_state.incident_to_remove = incident_id

        if st.session_state.confirm_remove:
            st.warning(f"Are you sure you want to proceed?\nAll data of incident '{st.session_state.incident_to_remove}' will be permanently removed.")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Yes"):
                    st.success("Deleting incident...")
                    self = SecurityIncident.get_self(incidents, int(incident_id))
                    success = incidents[self].save_changes("delete")
                    if success is not None:
                        st.success("Incident deletion successful!")
                        st.rerun()
                    else:
                        st.warning("Incident deletion unsuccessful!")

                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.incident_to_remove = ""

            with col_b:
                if st.button("No"):
                    st.info("Action cancelled.")
                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.incident_to_remove = ""

    # Update incident
    elif selected_categories == "Update Status":
        st.subheader("Update Incident Status")
        with st.form("update_status"):
            incident_id = st.text_input("Incident ID")
            check_id = st.form_submit_button("Check Incident ID")
            # Check if the incident is in the database
            if check_id:
                self = SecurityIncident.get_self(incidents, int(incident_id))
                if self is None:
                    st.error("Error: Invalid Incident ID.")
                else:
                    st.write(incidents[self])

            new_status = st.selectbox("New Status", ["Open", "Investigating", "Closed"])
            submitted = st.form_submit_button("Update Incident")

            if submitted:
                self = SecurityIncident.get_self(incidents, int(incident_id))
                incidents[self].update_status(new_status)
                incidents[self].save_changes("update")
                st.success(f"Incident {incident_id} updated successfully!")
                st.rerun()



# ---------- Data Science Display ----------
elif st.session_state.selected_categories == "Data Science":

    db = DatabaseManager("app/data/DATA/intelligence_platform.db")
    db.connect()

    st.subheader("IT Operations by departments who uploaded (Monthly)")

    col1, col2 = st.columns(2)
    # Group incidents by month and category
    chart_data = """
           SELECT strftime('%Y-%m', upload_date) as month, uploaded_by, COUNT(*) as count
           FROM datasets_metadata
           GROUP BY month, uploaded_by
           ORDER BY month
           """
    # Connects to database to run chart_data and to make a dataframe
    df = pd.read_sql_query(chart_data, conn)

    df_pivot = df.pivot(index="month", columns="uploaded_by", values="count").fillna(0)

    # Show bar chart
    with col1:
        st.subheader("Line chart")
        st.line_chart(df_pivot)

    # Show the line chart
    with col2:
        st.subheader("\nBar chart")
        st.bar_chart(df_pivot)

    rows = db.fetch_all(
        "SELECT dataset_id, name, rows, columns, uploaded_by, upload_date, reported_by FROM datasets_metadata ORDER BY dataset_id")

    datasets: list[Dataset] = []
    for row in rows:
        dataset = Dataset(
            db_path="app/data/DATA/intelligence_platform.db",
            dataset_id=row[0],
            name=row[1],
            rows=row[2],
            columns=row[3],
            source=row[4],
            upload_date=row[5],
            reported_by=row[6],
        )
        datasets.append(dataset)

    # Create DataFrame with named columns
    columns = ["dataset_id", "name", "rows", "columns", "uploaded_by", "upload_date", "reported_by"]
    df = pd.DataFrame(rows, columns=columns)

    # Show DataFrame
    with st.expander("See raw data"):
        st.dataframe(df)

    # Allow category selections
    edit_categories = ["Add", "Remove"]
    selected_categories = st.selectbox("Edit Data Science Datasets:", edit_categories)

    # Insert new dataset
    if selected_categories == "Add":
        st.subheader("Add New Dataset")
        with st.form("insert_form"):
            name = st.text_input("Department Name")
            rows = st.text_input("Row Number")
            columns = st.text_input("Column Number")
            uploaded_by = st.text_input("Uploaded By")
            upload_date = st.text_input("Created At (YYYY-MM-DD)")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Insert Ticket")

            if submitted:
                dataset = Dataset(
                    db_path="app/data/DATA/intelligence_platform.db",
                    dataset_id=None,
                    name=name,
                    rows=rows,
                    columns=columns,
                    source=uploaded_by,
                    upload_date=upload_date,
                    reported_by=reported_by,
                )

                dataset_id = dataset.save_changes("add")
                st.success(f"Dataset {dataset_id} inserted successfully!")
                st.rerun()

    # Remove dataset
    elif selected_categories == "Remove":
        # Ensure state keys exist
        if "confirm_remove" not in st.session_state:
            st.session_state.confirm_remove = False
        if "ticket_to_remove" not in st.session_state:
            st.session_state.dataset_to_remove = ""

        st.subheader("Remove Dataset")

        with st.form("remove_form"):
            dataset_id = st.text_input("Dataset ID")
            check_id = st.form_submit_button("Check Dataset ID")
            # Check if the dataset is in the database
            if check_id:
                if dataset_id.isdigit():
                    self = Dataset.get_self(datasets, int(dataset_id))
                    if self is None:
                        st.error("Error: Invalid Dataset ID.")
                    else:
                        st.write(datasets[self])
                else:
                    st.error("Error: Invalid Dataset ID.")

            submitted = st.form_submit_button("Remove Dataset")

            if submitted:
                # Move into confirmation mode and remember the ID
                st.session_state.confirm_remove = True
                st.session_state.dataset_to_remove = dataset_id

        if st.session_state.confirm_remove:
            st.warning(f"Are you sure you want to proceed?\nAll data of dataset '{st.session_state.dataset_to_remove}' will be permanently removed.")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Yes"):
                    st.success("Deleting dataset...")
                    self = Dataset.get_self(datasets, int(dataset_id))
                    success = datasets[self].save_changes("delete")
                    if success is not None:
                        st.success("Dataset deletion successful!")
                        st.rerun()
                    else:
                        st.warning("Dataset deletion unsuccessful!")

                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.dataset_to_remove = ""

            with col_b:
                if st.button("No"):
                    st.info("Action cancelled.")
                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.dataset_to_remove = ""


# ---------- IT Operations Display ----------
elif st.session_state.selected_categories == "IT Operations":

    db = DatabaseManager("app/data/DATA/intelligence_platform.db")
    db.connect()

    st.subheader("IT Operations by Status (Monthly)")

    col1, col2 = st.columns(2)
    # Group incidents by month and category
    chart_data = """
           SELECT strftime('%Y-%m', created_at) as month, status, COUNT(*) as count
           FROM it_tickets
           GROUP BY month, status
           ORDER BY month
           """
    # Connects to database to run chart_data and to make a dataframe
    df = pd.read_sql_query(chart_data, conn)

    df_pivot = df.pivot(index="month", columns="status", values="count").fillna(0)

    # Show bar chart
    with col1:
        st.subheader("Line chart")
        st.line_chart(df_pivot)

    # Show the line chart
    with col2:
        st.subheader("\nBar chart")
        st.bar_chart(df_pivot)

    rows = db.fetch_all(
        "SELECT ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by FROM it_tickets ORDER BY ticket_id")

    tickets: list[ITTicket] = []
    for row in rows:
        ticket = ITTicket(
            db_path= "app/data/DATA/intelligence_platform.db",
            ticket_id=row[0],
            priority=row[1],
            description=row[2],
            status=row[3],
            assigned_to=row[4],
            created_at=row[5],
            resolution_time_hours=row[6],
            reported_by=row[7],
        )
        tickets.append(ticket)

    columns = ["ticket_id", "priority", "description", "status", "assigned_to", "created_at", "resolution_time_hours", "reported_by"]
    df = pd.DataFrame(rows, columns=columns)

    # Show DataFrame
    with st.expander("See raw data"):
        st.dataframe(df)

    # Allow category selections
    edit_categories = ["Add", "Remove", "Update Status"]
    selected_categories = st.selectbox("Edit IT Tickets:", edit_categories)

    # Insert new tickit
    if selected_categories == "Add":
        st.subheader("Add New Ticket")
        with st.form("insert_form"):
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Description")
            status = st.selectbox("Status", ["In Progress", "Open", "Resolved", "Waiting for User"])
            assigned_to = st.selectbox("Assigned To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
            created_at = st.text_input("Created At (YYYY-MM-DD HH:MM:SS)")
            resolution_time_hours = st.text_input("Resolution Time (HH)")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Insert Ticket")

            if submitted:
                ticket = ITTicket(
                    db_path= "app/data/DATA/intelligence_platform.db",
                    ticket_id=None,
                    priority=priority,
                    description=description,
                    status=status,
                    assigned_to=assigned_to,
                    created_at=created_at,
                    resolution_time_hours=resolution_time_hours,
                    reported_by=reported_by,
                )

                ticket_id = ticket.save_changes("add")
                st.success(f"Ticket {ticket_id} inserted successfully!")
                st.rerun()

    # Remove ticket
    elif selected_categories == "Remove":
        # Ensure state keys exist
        if "confirm_remove" not in st.session_state:
            st.session_state.confirm_remove = False
        if "ticket_to_remove" not in st.session_state:
            st.session_state.ticket_to_remove = ""

        st.subheader("Remove Ticket")

        with st.form("remove_form"):
            ticket_id = st.text_input("Ticket ID")
            check_id = st.form_submit_button("Check Ticket ID")
            # Check if the ticket is in the database
            if check_id:
                if ticket_id.isdigit():
                    self = ITTicket.get_self(tickets, int(ticket_id))
                    if self is None:
                        st.error("Error: Invalid Dataset ID.")
                    else:
                        st.write(tickets[self])
                else:
                    st.error("Error: Invalid Dataset ID.")
            submitted = st.form_submit_button("Remove Ticket")

            if submitted:
                # Move into confirmation mode and remember the ID
                st.session_state.confirm_remove = True
                st.session_state.ticket_to_remove = ticket_id

        if st.session_state.confirm_remove:
            st.warning(f"Are you sure you want to proceed?\nAll data of ticket '{st.session_state.ticket_to_remove}' will be permanently removed.")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Yes"):
                    st.success("Deleting ticket...")
                    self = ITTicket.get_self(tickets, int(ticket_id))
                    success = tickets[self].save_changes("delete")
                    if success is not None:
                        st.success("Ticket deletion successful!")
                        st.rerun()
                    else:
                        st.warning("Ticket deletion unsuccessful!")

                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.ticket_to_remove = ""

            with col_b:
                if st.button("No"):
                    st.info("Action cancelled.")
                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.ticket_to_remove = ""

    # Update ticket
    elif selected_categories == "Update Status":
        st.subheader("Update Ticket Status")
        with st.form("update_status"):
            ticket_id = st.text_input("Ticket ID")
            check_id = st.form_submit_button("Check Ticket ID")
            # Check if the ticket is in the database
            if check_id:
                if ticket_id.isdigit():
                    self = ITTicket.get_self(tickets, int(ticket_id))
                    if self is None:
                        st.error("Error: Invalid Dataset ID.")
                    else:
                        st.write(tickets[self])
                else:
                    st.error("Error: Invalid Dataset ID.")
            new_status = st.selectbox("Status", ["In Progress", "Open", "Resolved", "Waiting for User"])
            submitted = st.form_submit_button("Update Ticket")

            if submitted:
                self = ITTicket.get_self(tickets, int(ticket_id))
                tickets[self].update_status(new_status)
                tickets[self].save_changes("update")
                st.success(f"Incident {ticket_id} updated successfully!")
                st.rerun()

    # st.subheader("IT Operations by Status (Monthly)")
    #
    # # load_csv_to_table(conn, "app/data/DATA/it_tickets.csv", "it_tickets")
    #
    # col1, col2 = st.columns(2)
    # # Group incidents by month and category
    # chart_data = """
    #        SELECT strftime('%Y-%m', created_at) as month, status, COUNT(*) as count
    #        FROM it_tickets
    #        GROUP BY month, status
    #        ORDER BY month
    #        """
    # # Connects to database to run chart_data and to make a dataframe
    # df = pd.read_sql_query(chart_data, conn)
    #
    # df_pivot = df.pivot(index="month", columns="status", values="count").fillna(0)
    #
    # # Show bar chart
    # with col1:
    #     st.subheader("Line chart")
    #     st.line_chart(df_pivot)
    #
    # # Show the line chart
    # with col2:
    #     st.subheader("\nBar chart")
    #     st.bar_chart(df_pivot)
    #
    # # Shows it_tickets data
    # data = get_all_tickets(conn)
    # with st.expander("See raw data"):
    #     st.dataframe(data)
    #
    # # Allow category selections
    # edit_categories = ["Add", "Remove", "Update Status"]
    # selected_categories = st.selectbox("Edit IT Tickets:", edit_categories)
    #
    # # Insert new tickit
    # if selected_categories == "Add":
    #     st.subheader("Add New Ticket")
    #     with st.form("insert_form"):
    #         priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
    #         description = st.text_area("Description")
    #         status = st.selectbox("Status", ["In Progress", "Open", "Resolved", "Waiting for User"])
    #         assigned_to = st.selectbox("Assigned To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
    #         created_at = st.text_input("Created At (YYYY-MM-DD HH:MM:SS)")
    #         resolution_time_hours = st.text_input("Resolution Time (HH)")
    #         reported_by = st.text_input("Reported By (optional)")
    #         submitted = st.form_submit_button("Insert Ticket")
    #
    #         if submitted:
    #             ticket_id = insert_ticket(conn, priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by)
    #             st.success(f"Ticket {ticket_id} inserted successfully!")
    #
    # # Remove ticket
    # elif selected_categories == "Remove":
    #     # Ensure state keys exist
    #     if "confirm_remove" not in st.session_state:
    #         st.session_state.confirm_remove = False
    #     if "ticket_to_remove" not in st.session_state:
    #         st.session_state.ticket_to_remove = ""
    #
    #     st.subheader("Remove Ticket")
    #
    #     with st.form("remove_form"):
    #         ticket_id = st.text_input("Ticket ID")
    #         submitted = st.form_submit_button("Remove Ticket")
    #
    #         if submitted:
    #             # Move into confirmation mode and remember the ID
    #             st.session_state.confirm_remove = True
    #             st.session_state.ticket_to_remove = ticket_id
    #
    #     if st.session_state.confirm_remove:
    #         st.warning(f"Are you sure you want to proceed?\nAll data of ticket '{st.session_state.ticket_to_remove}' will be permanently removed.")
    #         col_a, col_b = st.columns(2)
    #         with col_a:
    #             if st.button("Yes"):
    #                 st.success("Deleting ticket...")
    #                 success = delete_ticket(conn, st.session_state.ticket_to_remove)
    #                 if success == 1:
    #                     st.success("Ticket deletion successful!")
    #                 else:
    #                     st.warning("Ticket deletion unsuccessful!")
    #
    #                 # Reset state and clear input
    #                 st.session_state.confirm_remove = False
    #                 st.session_state.ticket_to_remove = ""
    #
    #         with col_b:
    #             if st.button("No"):
    #                 st.info("Action cancelled.")
    #                 # Reset state and clear input
    #                 st.session_state.confirm_remove = False
    #                 st.session_state.ticket_to_remove = ""
    #
    # # Update ticket
    # elif selected_categories == "Update Status":
    #     st.subheader("Update Ticket Status")
    #     with st.form("update_status"):
    #         ticket_id = st.text_input("Ticket ID")
    #         new_status = st.selectbox("Status", ["In Progress", "Open", "Resolved", "Waiting for User"])
    #         submitted = st.form_submit_button("Update Ticket")
    #
    #         if submitted:
    #             update_ticket_status(conn, ticket_id, new_status)
    #             st.success(f"Incident {ticket_id} updated successfully!")


# Logout button
with st.sidebar:
    st.divider()
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")