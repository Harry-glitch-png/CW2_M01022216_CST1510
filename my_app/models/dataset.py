from my_app.services.database_manager import DatabaseManager

#conn, name, rows, columns, uploaded_by, upload_date, reported_by=None
class Dataset(DatabaseManager):
    """Represents a data science dataset in the platform."""
    # Initializes the objects
    def __init__(self, db_path: str, dataset_id: int | None, name: str, rows: int, columns: int, source: str, upload_date: str | None, reported_by: str | None):
        super().__init__(db_path)
        self.__id = dataset_id
        self.__name = name
        self.__rows = rows
        self.__columns = columns
        self.__source = source
        self.__upload_date = upload_date
        self.__reported_by = reported_by

    # Get self
    def get_self(datasets: list["Dataset"], dataset_id: str) -> str | None:
        """Finds a dataset by its ID."""
        self = 0
        # Checks if the ID is in the datasets
        if dataset_id.isdigit(): # Checks if the ID is a digit
            for dataset in datasets:
                if dataset.__id == int(dataset_id):
                    return self
                self += 1
        return None

    # Get source
    def get_source(self) -> str:
        """Retrieves the dataset source."""
        return self.__source

    # Save changes
    def save_changes(self, change_type: str) -> int | None:
        """Add or delete the dataset into or from the database."""
        if change_type.lower() == "add":
            """Add a new dataset into the database."""
            # If user chose not to enter reported by
            if self.__reported_by == "":
                self.__reported_by = None
            # Parameterized SQL query to prevent SQL injection
            insert_sql = """
                    INSERT INTO datasets_metadata (name, rows, columns, uploaded_by, reported_by)
                    VALUES (?, ?, ?, ?, ?)
                    """

            # Execute the SQL statement
            cur = self.execute_query(
                insert_sql,
                (self.__name, self.__rows, self.__columns, self.__source, self.__reported_by,),
            )

            self.__id = cur.lastrowid
            return self.__id

        elif change_type.lower() == "delete":
            """Remove the dataset from the database."""
            # Parameterized DELETE query
            delete_sql = """
            DELETE FROM datasets_metadata
            WHERE dataset_id = ?
            """

            cur = self.execute_query(delete_sql,(self.__id,)) # Execute the SQL statement
            # Returns the ID
            self.__id = cur.lastrowid
            return self.__id

        return None

    def __str__(self) -> str:
        return f"Dataset {self.__id}: {self.__name}, row {self.__rows}, source [{self.__source}])"