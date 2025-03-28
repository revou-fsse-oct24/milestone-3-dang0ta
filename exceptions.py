class ConfigurationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Some required configurations are missing or not set properly: {self.message}"
    
    def __repr__(self):
        return f"ConfigurationError: {self.message}"

class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"An error occurred while interacting with the database: {self.message}"
    
    def __repr__(self):
        return f"DatabaseError: {self.message}"

class AuthenticationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AuthorizationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)