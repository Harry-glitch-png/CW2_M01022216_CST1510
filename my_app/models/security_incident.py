from my_app.services.database_manager import DatabaseManager

class SecurityIncident(DatabaseManager):
    """Represents a cybersecurity incident in the platform."""

    def __init__(self, db_path: str, incident_id: int | None, timestamp : str, incident_type: str, severity: str, status: str, description: str, reported_by=None,):
        super().__init__(db_path)
        self.__id = incident_id
        self.__timestamp = timestamp
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by

    def get_id(self) -> int:
        return self.__id

    def get_self(incidents: list["SecurityIncident"], incident_id: int) -> int | None:
        self = 0
        for incident in incidents:
            if incident.__id == incident_id:
                return self
            self += 1
        return None

    def get_timestamp(self) -> str:
        return self.__timestamp

    def get_severity(self) -> str:
        return self.__severity

    def get_status(self) -> str:
        return self.__status

    def get_description(self) -> str:
        return self.__description

    def get_reporter(self) -> str:
        return self.__reported_by

    def update_status(self, new_status: str) -> None:
        self.__status = new_status

    def get_severity_level(self) -> int:
        """Return an integer severity level (simple example)."""
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)

    def save_changes(self, change_type: str) -> int | None:
        """Add, delete or update the cybersecurity incident into the database."""
        if change_type.lower() == "add":
            """Add a new incident into the database."""
            # Parameterized SQL query to prevent SQL injection
            insert_sql = """
                        INSERT INTO cyber_incidents (timestamp, severity, category, status, description, reported_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """

            cur = self.execute_query(
                insert_sql,
                (self.__timestamp, self.__severity, self.__incident_type, self.__status, self.__description, self.__reported_by,),
            )

            self.__id = cur.lastrowid
            return self.__id

        elif change_type.lower() == "delete":
            """Remove the cybersecurity incident from the database."""
            # Parameterized DELETE query
            delete_sql = """
                DELETE FROM cyber_incidents
                WHERE incident_id = ?
                """

            cur = self.execute_query(delete_sql,(self.__id,))
            self.__id = cur.lastrowid
            return self.__id

        elif change_type.lower() == "update":
            """Update the cybersecurity incident status from the database."""

            # Parameterized UPDATE query
            update_sql = """
            UPDATE cyber_incidents
            SET status = ?
            WHERE incident_id = ?
            """

            cur = self.execute_query(update_sql,(self.__status, self.__id,))
            self.__id = cur.lastrowid
            return self.__id

        return None


    def __str__(self) -> str:
        return f"Incident {self.__id}, Type: {self.__incident_type}, [{self.__severity.upper()}], [{self.__status}], Description: {self.__description}"