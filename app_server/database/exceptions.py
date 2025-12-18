class SQLException(Exception):
    def __init__(self, message: str, sqlstate: str | None):
        super().__init__(message)
        self.message = message
        self.sqlstate = sqlstate

    def get_notify_message(self):
        return self.message if self.sqlstate == "45000" else "Internal server error"
