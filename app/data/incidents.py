import pandas as pd
from app.data.db import *
from app.data.schema import create_all_tables

conn = connect_database()

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

    cursor.execute(insert_sql, (timestamp, severity, category, status, description, reported_by))
    conn.commit()

    incident_id = cursor.lastrowid
    return incident_id


def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.

    Returns:
        pandas.DataFrame: All incidents
    """

    # Use pandas to execute SQL and return a DataFrame
    df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    return df


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

    cursor.execute(update_sql, (new_status, incident_id))
    conn.commit()

    print(f"✅ Incident {incident_id} status updated to '{new_status}'.")
    return cursor.rowcount  # Number of rows affected


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

    cursor.execute(delete_sql, (incident_id,))
    conn.commit()

    print(f"✅ Incident {incident_id} deleted successfully.")
    return cursor.rowcount  # Number of rows affected (should be 1 if successful)


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

# # Test: Run analytical queries
# conn = connect_database()
#
# print("\n Incidents by Type:")
# df_by_type = get_incidents_by_type_count(conn)
# print(df_by_type)
#
# print("\n High Severity Incidents by Status:")
# df_high_severity = get_high_severity_by_status(conn)
# print(df_high_severity)
#
# print("\n Incident Types with Many Cases (>5):")
# df_many_cases = get_incident_types_with_many_cases(conn, min_count=5)
# print(df_many_cases)
#
# conn.close()