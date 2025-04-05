class ConfigurationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Some required configurations are missing or not set properly: {self.message}"
    
    def __repr__(self):
        return f"ConfigurationError: {self.message}"
