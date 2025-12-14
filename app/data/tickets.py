import pandas as pd
from app.data.db import connect_database

conn = connect_database()

# Inset ticket
def insert_ticket(conn, priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by=None):
    """
    Insert a new IT ticket into the database.

    Args:
        conn: Database connection
        priority TEXT,
        description TEXT,
        status TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolution_time_hours TEXT
        reported_by: Username of reporter (optional)

    Returns:
        int: ID of the inserted ticket
    """

    cursor = conn.cursor()

    # Parameterized SQL query to prevent SQL injection
    insert_sql = """
            INSERT INTO it_tickets (priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

    cursor.execute(insert_sql, (priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Return ticket id
    ticket_id = cursor.lastrowid
    return ticket_id

# Get all tickets
def get_all_tickets(conn):
    """
    Retrieve all tickets from the database.

    Returns:
        pandas.DataFrame: All tickets
    """

    # Use pandas to execute SQL and return a DataFrame
    df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
    return df

# Update ticket status
def update_ticket_status(conn, ticket_id, new_status):
    """
    Update the status of a ticket.
    """

    cursor = conn.cursor()

    # Parameterized UPDATE query
    update_sql = """
    UPDATE it_tickets
    SET status = ?
    WHERE incident_id = ?
    """

    cursor.execute(update_sql, (new_status, ticket_id))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Varify status update
    print(f"✅ Ticket {ticket_id} status updated to '{new_status}'.")
    return cursor.rowcount  # Number of rows affected

# Delete ticket
def delete_ticket(conn, ticket_id):
    """
    Delete a ticket from the database.
    """

    cursor = conn.cursor()

    # Parameterized DELETE query
    delete_sql = """
    DELETE FROM it_tickets
    WHERE tickets_id = ?
    """

    cursor.execute(delete_sql, (ticket_id,))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Varify that the ticket is deleted
    print(f"✅ Ticket {ticket_id} deleted successfully.")
    return cursor.rowcount  # Number of rows affected

# Get ticket by priority count
def get_ticket_by_priority_count(conn):
    """
    Count tickets by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT ticket_id, COUNT(*) as count
    FROM it_tickets
    GROUP BY priority
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

# Get high priority by status
def get_high_priority_by_status(conn):
    """
    Count open tickets by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    WHERE priority = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

# Get ticket types with many cases
def get_ticket_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT ticket_id, COUNT(*) as count
    FROM it_tickets
    GROUP BY status
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df