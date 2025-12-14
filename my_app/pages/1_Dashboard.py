import streamlit as st
import pandas as pd
import numpy as np
from time import sleep as pause
from app.data.db import connect_database
from my_app.services.database_manager import DatabaseManager
from my_app.models.security_incident import SecurityIncident
from my_app.models.dataset import Dataset
from my_app.models.it_ticket import ITTicket

st.set_page_config(page_title="Dashboard", page_icon="📊 ",
layout="wide")

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

    # Connects databases
    db = DatabaseManager("app/data/DATA/intelligence_platform.db")
    db.connect()

    st.subheader("Cyber Incidents by Category (Monthly):")

    col1, col2 = st.columns(2)
    # Group incidents by month and category for chart data
    chart_data = """
           SELECT strftime('%Y-%m', timestamp) as month, category, COUNT(*) as count
           FROM cyber_incidents
           GROUP BY month, category
           ORDER BY month
           """
    # Connects to database to run chart_data and to make a dataframe
    df = pd.read_sql_query(chart_data, conn)

    # Plots the charts
    df_pivot = df.pivot(index="month", columns="category", values="count").fillna(0)

    # Show bar chart
    with col1:
        st.subheader("Line chart")
        st.line_chart(df_pivot)

    # Show the line chart
    with col2:
        st.subheader("\nBar chart")
        st.bar_chart(df_pivot)

    # Makes a dataframe from the cyber_incidents database
    rows = db.fetch_all(
        "SELECT incident_id, timestamp, severity, category, status, description, reported_by FROM cyber_incidents ORDER BY incident_id")

    # Takes the rows dataframe and turns it into a list of objects for the SecurityIncident class.
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
        """Adds the incident to the database"""
        st.subheader("Add New Incident")
        # Creates a form for the user to insert a new incident into the database
        with st.form("insert_form"):
            severity = st.selectbox("Severity", ["Low", "Medium", "High"])
            category = st.selectbox("Category", ["DDos", "Malware", "Misconfiguration", "Phishing", "Unauthorized Access"])
            status = st.selectbox("Status", ["Open", "Investigating", "Closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Insert Incident")

            # Inserts the new incident
            if submitted:
                incident = SecurityIncident(
                    db_path= "app/data/DATA/intelligence_platform.db",
                    incident_id=None,
                    timestamp=None,
                    severity=severity,
                    incident_type=category,
                    status=status,
                    description=description,
                    reported_by=reported_by,
                )

                incident_id = incident.save_changes("add")
                st.success(f"Incident {incident_id} inserted successfully!")
                pause(2.5)  # Delay the page rerun
                st.rerun()  # Rerun the page

    # Remove incident
    elif selected_categories == "Remove":
        """Removes the incident from the database"""
        # Ensure state keys exist
        if "confirm_remove" not in st.session_state:
            st.session_state.confirm_remove = False
        if "incident_to_remove" not in st.session_state:
            st.session_state.incident_to_remove = ""

        st.subheader("Remove Incident")

        # Creates a form for the user so they can choose an incident to delete
        with st.form("remove_form"):
            incident_id = st.text_input("Incident ID")
            check_id = st.form_submit_button("Check Incident ID")
            # Check if the incident is in the database
            if check_id:
                self = SecurityIncident.get_self(incidents, incident_id)
                if self is None:
                    st.error("Error: Invalid Incident ID.")
                else:
                    st.write(incidents[self])

            submitted = st.form_submit_button("Remove Incident")

            if submitted:
                # Move into confirmation mode and remember the ID
                st.session_state.confirm_remove = True
                st.session_state.incident_to_remove = incident_id

        # Warns the user to make sure they want to delete the incident
        if st.session_state.confirm_remove:
            st.warning(f"Are you sure you want to proceed?\nAll data of incident '{st.session_state.incident_to_remove}' will be permanently removed.")
            col_a, col_b = st.columns(2)
            with col_a:
                # Deletes the incident
                if st.button("Yes"):
                    st.success("Deleting incident...")
                    self = SecurityIncident.get_self(incidents, incident_id)
                    pause(2.5) # Delay the output
                    if self is None:
                        st.error("Error: Invalid Incident ID.")
                    else:
                        success = incidents[self].save_changes("delete")
                        if success is not None:
                            st.success("Incident deletion successful!")
                        else:
                            st.warning("Incident deletion unsuccessful!")

                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.incident_to_remove = ""
                    pause(2.5) # Delay the page rerun
                    st.rerun() # Rerun the page

            # Keep the incident
            with col_b:
                if st.button("No"):
                    st.info("Action cancelled.")
                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.incident_to_remove = ""
                    pause(2.5) # Delay the page rerun
                    st.rerun() # Rerun the page

    # Update incident
    elif selected_categories == "Update Status":
        """Updates the status of the incident"""
        st.subheader("Update Incident Status")
        # Creates a from for the user to use to update the status
        with st.form("update_status"):
            incident_id = st.text_input("Incident ID")
            check_id = st.form_submit_button("Check Incident ID")
            # Check if the incident is in the database
            if check_id:
                self = SecurityIncident.get_self(incidents, incident_id)
                if self is None:
                    st.error("Error: Invalid Incident ID.")
                else:
                    st.write(incidents[self])

            new_status = st.selectbox("New Status", ["Open", "Investigating", "Closed"])
            submitted = st.form_submit_button("Update Incident")

            # Updates the status
            if submitted:
                self = SecurityIncident.get_self(incidents, incident_id)
                if self is None:
                    st.error("Error: Invalid Incident ID.")
                else:
                    incidents[self].update_status(new_status)
                    incidents[self].save_changes("update")
                    st.success(f"Incident {incident_id} updated successfully!")
                    pause(5) # Delay the page rerun
                    st.rerun() # Rerun page


# ---------- Data Science Display ----------
elif st.session_state.selected_categories == "Data Science":

    # Connect database
    db = DatabaseManager("app/data/DATA/intelligence_platform.db")
    db.connect()

    st.subheader("Datasets by departments who uploaded (Monthly)")

    col1, col2 = st.columns(2)
    # Group datasets by month and who uploaded
    chart_data = """
           SELECT strftime('%Y-%m', upload_date) as month, uploaded_by, COUNT(*) as count
           FROM datasets_metadata
           GROUP BY month, uploaded_by
           ORDER BY month
           """
    # Connects to database to run chart_data and to make a dataframe
    df = pd.read_sql_query(chart_data, conn)

    # Plots the charts
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

    # Takes the rows dataframe and turns it into a list of objects for the Dataset class.
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
        # Creates a form for the user to insert a new dataset into the database
        with st.form("insert_form"):
            name = st.text_input("Department Name")
            rows = st.text_input("Row Number")
            columns = st.text_input("Column Number")
            uploaded_by = st.text_input("Uploaded By")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Insert Ticket")

            # Checks if required fields are filled
            if submitted:
                if name or rows or columns or uploaded_by == "":
                    st.error("Error: Please fill all necessary fields.")
                else:
                    # Inserts the new incident
                    dataset = Dataset(
                        db_path="app/data/DATA/intelligence_platform.db",
                        dataset_id=None,
                        name=name,
                        rows=rows,
                        columns=columns,
                        source=uploaded_by,
                        upload_date=None,
                        reported_by=reported_by,
                    )

                    dataset_id = dataset.save_changes("add")
                    st.success(f"Dataset {dataset_id} inserted successfully!")
                pause(2.5)  # Delay the page rerun
                st.rerun()  # Rerun the page

    # Remove dataset
    elif selected_categories == "Remove":
        # Ensure state keys exist
        if "confirm_remove" not in st.session_state:
            st.session_state.confirm_remove = False
        if "ticket_to_remove" not in st.session_state:
            st.session_state.dataset_to_remove = ""

        st.subheader("Remove Dataset")

        # Creates a form for the user so they can choose a dataset to delete
        with st.form("remove_form"):
            dataset_id = st.text_input("Dataset ID")
            check_id = st.form_submit_button("Check Dataset ID")
            # Check if the dataset is in the database
            if check_id:
                self = Dataset.get_self(datasets, dataset_id)
                if self is None:
                    st.error("Error: Invalid Dataset ID.")
                else:
                    st.write(datasets[self])


            submitted = st.form_submit_button("Remove Dataset")

            if submitted:
                # Move into confirmation mode and remember the ID
                st.session_state.confirm_remove = True
                st.session_state.dataset_to_remove = dataset_id

        if st.session_state.confirm_remove:
            # Warns the user to make sure they want to delete the dataset
            st.warning(f"Are you sure you want to proceed?\nAll data of dataset '{st.session_state.dataset_to_remove}' will be permanently removed.")
            col_a, col_b = st.columns(2)
            with col_a:
                # Deletes dataset
                if st.button("Yes"):
                    st.success("Deleting dataset...")
                    self = Dataset.get_self(datasets, dataset_id)
                    pause(2.5) # Delay the output
                    if self is None:
                        st.error("Error: Invalid Dataset ID.")
                    else:
                        success = datasets[self].save_changes("delete")
                        if success is not None:
                            st.success("Dataset deletion successful!")
                        else:
                            st.warning("Dataset deletion unsuccessful!")

                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.dataset_to_remove = ""
                    pause(2.5) # Delay the page rerun
                    st.rerun() # Rerun the page

            with col_b:
                # Keep dataset
                if st.button("No"):
                    st.info("Action cancelled.")
                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.dataset_to_remove = ""
                    pause(2.5) # Delay the page rerun
                    st.rerun() # Rerun the page


# ---------- IT Operations Display ----------
elif st.session_state.selected_categories == "IT Operations":

    # Connect database
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

    # Plot charts
    df_pivot = df.pivot(index="month", columns="status", values="count").fillna(0)

    # Show bar chart
    with col1:
        st.subheader("Line chart")
        st.line_chart(df_pivot)

    # Show the line chart
    with col2:
        st.subheader("\nBar chart")
        st.bar_chart(df_pivot)

    # Makes a dataframe from the cyber_incidents database
    rows = db.fetch_all(
        "SELECT ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by FROM it_tickets ORDER BY ticket_id")

    # Takes the rows dataframe and turns it into a list of objects for the ITTicket class.
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

    # Create DataFrame with named columns
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
        # Creates a form for the user to insert a new ticket into the database
        with st.form("insert_form"):
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Description")
            status = st.selectbox("Status", ["In Progress", "Open", "Resolved", "Waiting for User"])
            assigned_to = st.selectbox("Assigned To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
            resolution_time_hours = st.text_input("Resolution Time (HH)")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Insert Ticket")

            if submitted:
                # Inserts the new incident
                ticket = ITTicket(
                    db_path= "app/data/DATA/intelligence_platform.db",
                    ticket_id=None,
                    priority=priority,
                    description=description,
                    status=status,
                    assigned_to=assigned_to,
                    created_at=None,
                    resolution_time_hours=resolution_time_hours,
                    reported_by=reported_by,
                )

                ticket_id = ticket.save_changes("add")
                st.success(f"Ticket {ticket_id} inserted successfully!")
                pause(2.5)  # Delay the page rerun
                st.rerun()  # Rerun the page

    # Remove ticket
    elif selected_categories == "Remove":
        # Ensure state keys exist
        if "confirm_remove" not in st.session_state:
            st.session_state.confirm_remove = False
        if "ticket_to_remove" not in st.session_state:
            st.session_state.ticket_to_remove = ""

        st.subheader("Remove Ticket")
        # Creates a form for the user so they can choose a ticket to delete
        with st.form("remove_form"):
            ticket_id = st.text_input("Ticket ID")
            check_id = st.form_submit_button("Check Ticket ID")
            # Check if the ticket is in the database
            if check_id:
                self = ITTicket.get_self(tickets, ticket_id)
                if self is None:
                    st.error("Error: Invalid Dataset ID.")
                else:
                    st.write(tickets[self])

            submitted = st.form_submit_button("Remove Ticket")

            if submitted:
                # Move into confirmation mode and remember the ID
                st.session_state.confirm_remove = True
                st.session_state.ticket_to_remove = ticket_id

        if st.session_state.confirm_remove:
            # Warns the user to make sure they want to delete the ticket
            st.warning(f"Are you sure you want to proceed?\nAll data of ticket '{st.session_state.ticket_to_remove}' will be permanently removed.")
            col_a, col_b = st.columns(2)
            with col_a:
                # Deletes the ticket
                if st.button("Yes"):
                    st.success("Deleting ticket...")
                    self = ITTicket.get_self(tickets, ticket_id)
                    pause(2.5) # Delay the output
                    if self is None:
                        st.error("Error: Invalid Dataset ID.")
                    else:
                        success = tickets[self].save_changes("delete")
                        if success is not None:
                            st.success("Ticket deletion successful!")
                        else:
                            st.warning("Ticket deletion unsuccessful!")

                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.ticket_to_remove = ""
                    pause(2.5) # Delay the page rerun
                    st.rerun() # Rerun the page

            with col_b:
                # Keep ticket
                if st.button("No"):
                    st.info("Action cancelled.")
                    # Reset state and clear input
                    st.session_state.confirm_remove = False
                    st.session_state.ticket_to_remove = ""
                    pause(2.5) # Delay the page rerun
                    st.rerun() # Rerun the page

    # Update ticket
    elif selected_categories == "Update Status":
        st.subheader("Update Ticket Status")
        # Creates a from for the user to use to update the status
        with st.form("update_status"):
            ticket_id = st.text_input("Ticket ID")
            check_id = st.form_submit_button("Check Ticket ID")
            # Check if the ticket is in the database
            if check_id:
                self = ITTicket.get_self(tickets, ticket_id)
                if self is None:
                    st.error("Error: Invalid Dataset ID.")
                else:
                    st.write(tickets[self])

            new_status = st.selectbox("Status", ["In Progress", "Open", "Resolved", "Waiting for User"])
            submitted = st.form_submit_button("Update Ticket")

            if submitted:
                # Updates the status
                self = ITTicket.get_self(tickets, int(ticket_id))
                if self is None:
                    st.error("Error: Invalid Dataset ID.")
                else:
                    tickets[self].update_status(new_status)
                    tickets[self].save_changes("update")
                    st.success(f"Incident {ticket_id} updated successfully!")
                pause(2.5)  # Delay the page rerun
                st.rerun()  # Rerun the page


# Logout button
with st.sidebar:
    st.divider()
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")