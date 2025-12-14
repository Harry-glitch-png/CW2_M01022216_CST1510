import pandas as pd
from app.data.db import *

conn = connect_database()

# Insert incident
def insert_incident(conn, timestamp, severity, category, status, description, reported_by=None):
    """
    Insert a new cyber incident into the database.

    Args:
        conn: Database connection
        date: Incident date (YYYY-MM-DD)
        incident_type: Type of incident
        severity: Severity level
        status: Current status
        description: Incident description
        reported_by: Username of reporter (optional)

    Returns:
        int: ID of the inserted incident
    """

    cursor = conn.cursor()

    # Parameterized SQL query to prevent SQL injection
    insert_sql = """
            INSERT INTO cyber_incidents (timestamp, severity, category, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """

    cursor.execute(insert_sql, (timestamp, severity, category, status, description, reported_by))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Return incident ID
    incident_id = cursor.lastrowid
    return incident_id

# Get all incidents
def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.

    Returns:
        pandas.DataFrame: All incidents
    """

    # Use pandas to execute SQL and return a DataFrame
    df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    return df

# Update incident status
def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    """

    cursor = conn.cursor()

    # Parameterized UPDATE query
    update_sql = """
    UPDATE cyber_incidents
    SET status = ?
    WHERE incident_id = ?
    """

    cursor.execute(update_sql, (new_status, incident_id))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Varify updated status
    print(f"✅ Incident {incident_id} status updated to '{new_status}'.")
    return cursor.rowcount  # Number of rows affected

# Delete incident
def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    """

    cursor = conn.cursor()

    # Parameterized DELETE query
    delete_sql = """
    DELETE FROM cyber_incidents
    WHERE incident_id = ?
    """

    cursor.execute(delete_sql, (incident_id,))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Varify that the incident is deleted
    print(f"✅ Incident {incident_id} deleted successfully.")
    return cursor.rowcount  # Number of rows affected (should be 1 if successful)

# Get incidents by type count
def get_incidents_by_type_count(conn):
    """
    Count incidents by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT category, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY category 
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

# Get high severity status
def get_high_severity_by_status(conn):
    """
    Count high severity incidents by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

# Get incident types with many cases
def get_incident_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT category, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY category
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df