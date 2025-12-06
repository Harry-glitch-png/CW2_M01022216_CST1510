from my_app.services.database_manager import DatabaseManager

#conn, name, rows, columns, uploaded_by, upload_date, reported_by=None
class Dataset(DatabaseManager):
    """Represents a data science dataset in the platform."""
    def __init__(self, db_path: str, dataset_id: int | None, name: str, rows: int, columns: int, source: str, upload_date: str, reported_by=None):
        super().__init__(db_path)
        self.__id = dataset_id
        self.__name = name
        self.__rows = rows
        self.__columns = columns
        self.__source = source
        self.__upload_date = upload_date
        self.__reported_by = reported_by

    def get_self(datasets: list["Dataset"], dataset_id) -> str | None:
        self = 0
        for dataset in datasets:
            if dataset.__id == dataset_id:
                return self
            self += 1
        return None

    def get_source(self) -> str:
        return self.__source

    def save_changes(self, change_type: str) -> int | None:
        """Add or delete the dataset into or from the database."""
        if change_type.lower() == "add":
            """Add a new dataset into the database."""
            # Parameterized SQL query to prevent SQL injection
            insert_sql = """
                    INSERT INTO datasets_metadata (name, rows, columns, uploaded_by, upload_date, reported_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """

            cur = self.execute_query(
                insert_sql,
                (self.__name, self.__rows, self.__columns, self.__source, self.__upload_date, self.__reported_by,),
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

            cur = self.execute_query(delete_sql,(self.__id,))
            self.__id = cur.lastrowid
            return self.__id

        return None

    def __str__(self) -> str:
        return f"Dataset {self.__id}: {self.__name}, row {self.__rows}, source [{self.__source}])"