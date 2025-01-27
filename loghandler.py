import os
from datetime import datetime

class LogHandler:
    def __init__(self):
        """
        Initializes the log handler.
        """
        self.log_file_path = "log.txt"
        self.file = open(self.log_file_path, "a") # open the log file in append mode (create it if it doesn't exist)

    def log(self, message, type):
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

        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.file.write(f"[{type}] {timestamp} -> {message}\n")

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
            self.file.close() # close the file
            self.file = open(self.log_file_path, "w") # open the file in write mode (clears it) 
            self.file.close() # close the file
            self.file = open(self.log_file_path, "a") # open the file in append mode back again
        except OSError as e:
            print(f"Error clearing log file: {e}")
        
    def close(self): #TODO implement close on window close
        """
        Closes the log file.

        params:
            None
        raises: 
            None
        returns:
            None
        """
        self.file.close()