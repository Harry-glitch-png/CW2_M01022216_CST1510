from my_app.services.database_manager import DatabaseManager

class SecurityIncident(DatabaseManager):
    """Represents a cybersecurity incident in the platform."""
    # Initializes the objects
    def __init__(self, db_path: str, incident_id: int | None, timestamp : str | None, incident_type: str, severity: str, status: str, description: str, reported_by: str | None):
        super().__init__(db_path)
        self.__id = incident_id
        self.__timestamp = timestamp
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by

    # Get ID
    def get_id(self) -> int:
        """Return the cybersecurity incident ID."""
        return self.__id

    # Get self
    def get_self(incidents: list["SecurityIncident"], incident_id: str) -> int | None:
        """Get the cybersecurity incident using the ID"""
        self = 0
        # Checks if the ID is in the incidents
        if incident_id.isdigit(): # Checks if the ID is a digit
            for incident in incidents:
                if incident.__id == int(incident_id):
                    return self
                self += 1
        return None

    # Get timestamp
    def get_timestamp(self) -> str:
        """Return the cybersecurity incident timestamp."""
        return self.__timestamp

    # Get severity
    def get_severity(self) -> str:
        """Return the cybersecurity incident severity."""
        return self.__severity

    # Get status
    def get_status(self) -> str:
        """Return the cybersecurity incident status."""
        return self.__status

    # Get description
    def get_description(self) -> str:
        """Return the cybersecurity incident description."""
        return self.__description

    # Get reporter
    def get_reporter(self) -> str:
        """Return the cybersecurity incident reporter name."""
        return self.__reported_by

    # Update status
    def update_status(self, new_status: str) -> None:
        """Updates the cybersecurity incident status."""
        self.__status = new_status

    # Get severity level
    def get_severity_level(self) -> int:
        """Return an integer severity level (simple example)."""
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)

    # Save changes
    def save_changes(self, change_type: str) -> int | None:
        """Add, delete or update the cybersecurity incident into the database."""
        if change_type.lower() == "add":
            """Add a new incident into the database."""
            # If user chose not to enter reported by
            if self.__reported_by == "":
                self.__reported_by = None

            # Parameterized SQL query to prevent SQL injection
            insert_sql = """
                        INSERT INTO cyber_incidents (severity, category, status, description, reported_by)
                        VALUES (?, ?, ?, ?, ?)
                        """

            # Execute the SQL statement
            cur = self.execute_query(
                insert_sql,
                (self.__severity, self.__incident_type, self.__status, self.__description, self.__reported_by,),
            )

            # Return ID
            self.__id = cur.lastrowid
            return self.__id

        elif change_type.lower() == "delete":
            """Remove the cybersecurity incident from the database."""
            # Parameterized DELETE query
            delete_sql = """
                DELETE FROM cyber_incidents
                WHERE incident_id = ?
                """

            cur = self.execute_query(delete_sql,(self.__id,)) # Execute the SQL statement
            # Return ID
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

            cur = self.execute_query(update_sql,(self.__status, self.__id,)) # Execute the SQL statement
            # Return ID
            self.__id = cur.lastrowid
            return self.__id

        return None


    def __str__(self) -> str:
        return f"Incident {self.__id}, Type: {self.__incident_type}, [{self.__severity.upper()}], [{self.__status}], Description: {self.__description}"