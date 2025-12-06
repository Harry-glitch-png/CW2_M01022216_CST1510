from my_app.services.database_manager import DatabaseManager

class ITTicket(DatabaseManager):
    """Represents an IT support ticket."""

    def __init__(self, db_path: str, ticket_id: int | None, priority: str, description: str, status: str, assigned_to: str, created_at: str, resolution_time_hours: str, reported_by=None):
        super().__init__(db_path)
        self.__id = ticket_id
        self.__priority = priority
        self.__description = description
        self.__status = status
        self.__assigned_to = assigned_to
        self.__created_at = created_at
        self.__resolution_time_hours = resolution_time_hours
        self.__reported_by = reported_by


    def get_id(self) -> str:
        return self.__id

    def get_self(tickets: list["ITTicket"], ticket_id: int) -> int | None:
        self = 0
        for ticket in tickets:
            if ticket.__id == ticket_id:
                return self
            self += 1
        return None

    def assign_to(self, staff: str) -> None:
        self.__assigned_to = staff

    def close_ticket(self) -> None:
        self.__status = "Closed"

    def get_status(self) -> str:
        return self.__status

    def update_status(self, new_status: str) -> None:
        self.__status = new_status

    def save_changes(self, change_type: str) -> int | None:
        """Add, delete or update the IT ticket into or from the database."""
        if change_type.lower() == "add":
            """Add a new IT ticket into the database."""
            # Parameterized SQL query to prevent SQL injection
            insert_sql = """
                    INSERT INTO it_tickets (priority, description, status, assigned_to, created_at, resolution_time_hours, reported_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """

            cur = self.execute_query(
                insert_sql,
                (self.__priority, self.__description, self.__status, self.__assigned_to, self.__created_at, self.__resolution_time_hours, self.__reported_by),
            )

            self.__id = cur.lastrowid
            return self.__id

        elif change_type.lower() == "delete":
            """Remove the IT ticket from the database."""
            # Parameterized DELETE query
            delete_sql = """
            DELETE FROM it_tickets
            WHERE ticket_id = ?
            """

            cur = self.execute_query(delete_sql,(self.__id,))
            self.__id = cur.lastrowid
            return self.__id

        elif change_type.lower() == "update":
            """Update the IT ticket status from the database."""

            # Parameterized UPDATE query
            update_sql = """
                UPDATE it_tickets
                SET status = ?
                WHERE ticket_id = ?
                """

            cur = self.execute_query(update_sql,(self.__status, self.__id,))
            self.__id = cur.lastrowid
            return self.__id

        return None

    def __str__(self) -> str:
        return (
        f"Ticket {self.__id} "
        f"[{self.__priority}] – {self.__status} (assigned to: {self.__assigned_to})"
        )