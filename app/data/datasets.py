import pandas as pd
from app.data.db import connect_database

conn = connect_database()

# Insert dataset
def insert_dataset(conn, name, rows, columns, uploaded_by, upload_date, reported_by=None):
    """
    Insert a new dataset into the database.

    Args:
        conn: Database connection
        name TEXT NOT NULL,
        rows TEXT,
        columns TEXT,
        uploaded_by TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        reported_by: Username of reporter (optional)

    Returns:
        int: ID of the inserted dataset
    """

    cursor = conn.cursor()

    # Parameterized SQL query to prevent SQL injection
    insert_sql = """
            INSERT INTO datasets_metadata (name, rows, columns, uploaded_by, upload_date, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """

    cursor.execute(insert_sql, (name, rows, columns, uploaded_by, upload_date, reported_by)) # Execute the SQL statement
    conn.commit() # Save inserted data

    # Provides the incident ID
    incident_id = cursor.lastrowid
    return incident_id

# Get all datasets
def get_all_datasets(conn):
    """
    Retrieve all datasets from the database.

    Returns:
        pandas.DataFrame: All datasets
    """

    # Use pandas to execute SQL and return a DataFrame
    df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn) # Execute the SQL statement
    return df

# Delete dataset
def delete_dataset(conn, dataset_id):
    """
    Delete a dataset from the database.
    """

    cursor = conn.cursor()

    # Parameterized DELETE query
    delete_sql = """
    DELETE FROM datasets_metadata
    WHERE datasets_metadata = ?
    """

    cursor.execute(delete_sql, (dataset_id,))# Execute the SQL statement
    conn.commit() # Save inserted data

    # Varify deletion
    print(f"✅ Dataset {dataset_id} deleted successfully.")
    return cursor.rowcount  # Number of rows affected