import logging

class LogHandler:
    def __init__(self):
        """
        Initializes the log handler.
        """
        self.log_file_path = "log.txt"
        self.logger = logging.getLogger("async_logger")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_file_path)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.handler = handler

    async def log(self, message, type):
        """
        Logs a message to the log file.
        
        params:
            message: str The message to log.
            type: str The type of message to log.
        raises:
            None    
        returns:
            None
        """
        if type == "INFO":
            self.logger.info(message)
        elif type == "ERROR":
            self.logger.error(message)
        elif type == "WARNING":
            self.logger.warning(message)
        elif type == "DEBUG":
            self.logger.debug(message)

    def clear(self):
        """
        Clears the log file.
        
        params:
            None
        returns:
            None
        raises:
            OSError if file procedures fail
        """
        try:
            self.handler.close()  # Close the current handler
            self.logger.removeHandler(self.handler)  # Remove the handler from the logger
            with open(self.log_file_path, "w") as file:
                file.truncate(0)  # Clear the file contents
            self.logger.addHandler(self.handler)  # Re-add the handler to the logger
        except OSError as ex:
            print(f"Error clearing log file: {ex}")

    def close(self):
        """
        Closes the log file.

        params:
            None
        raises: 
            None
        returns:
            None
        """
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)