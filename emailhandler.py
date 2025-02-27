import os, json
from config import EMAIL_CONFIG, VERSION, WINDOW_RESOLUTION, REPO_URL
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from utils import create_button, create_img

try:
    from CTkMessagebox import CTkMessagebox
    from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    os.system("pip install -r requirements.txt")   
    from CTkMessagebox import CTkMessagebox
    from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

class EmailHandler:
    def __init__(self, log_handler):
        self.email_address = EMAIL_CONFIG["email_address"]
        self.recipient_email = "pmarini72107@gmail.com"
        self.log_handler = log_handler

        self.msg = MIMEMultipart()
        self.msg['From'] = self.email_address
        self.msg['To'] = self.recipient_email

        self.credentials: Credentials = None

        self.server = SMTP_SSL('smtp.gmail.com', 465) # SMTP server for Gmail
        self.server.ehlo()  # Identify the client to the server

    def load_credentials(self):
        creds: Credentials = None
        token_path: str = 'token.json'
        if os.path.exists(token_path):
            with open(token_path, 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token))
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise ValueError("Invalid or expired credentials. Please authenticate again.")
        return creds

    def send_bug_report(self, title, body, message_box_root_window, mode="config-credentials"):
        """
        Send a bug report via email.

        params:
            title (str): The title of the bug report.
            body (str): The body of the bug report.
            message_box_root_window (Tk): The root window of the application.
            mode (str): The mode of the bug report. Default is "config-credentials". Can be "config-credentials" or "google-auth".
        """
        self.msg['Subject'] = f"[Tracer Bug Report] {title} - V{VERSION} - {datetime.today().strftime('%Y-%m-%d')}"
        self.msg.attach(MIMEText(body, 'plain'))

        try:
            # Gather credentials
            if EMAIL_CONFIG["email_address"] == "": self.show_email_window(root=message_box_root_window)
            if mode == "config-credentials":
                if EMAIL_CONFIG["email_password"] == "": self.show_password_window(root=message_box_root_window)
                self.server.login(self.email_address, EMAIL_CONFIG["email_password"])
            elif mode == "google-auth":
                self.credentials: Credentials = self.load_credentials()
                self.server.login(self.email_address, self.credentials.token)

            # Send the email
            text = self.msg.as_string()
            self.server.sendmail(self.email_address, self.recipient_email, text)

            # Show a success message
            message_box: CTkMessagebox = CTkMessagebox(master=message_box_root_window, 
                                title="Success",
                                message="Bug report sent successfully.",
                                icon="check", 
                                options=["Close", "Send another"],
                                justify="center")
            self.log_handler.log(message=f"Bug report sent successfully with email: {self.email_address}.", type="INFO")
        except Exception as ex:
            message_box: CTkMessagebox = CTkMessagebox(master=message_box_root_window, 
                                title="Error while sending bug report",
                                message=f"An error occurred while sending the bug report.\n{str(ex)}", 
                                icon="error", 
                                options=["Close", "Retry"],
                                justify="center")
            self.log_handler.log(message=f"An error occurred while sending the bug report.\n{str(ex)}", type="ERROR")

    # Helper function to update the password TODO figure out if this properly updates at runtime
    def update_email(email, email_window):
        EMAIL_CONFIG["email_address"] = email
        email_window.destroy()

    # Helper function to update the password TODO figure out if this properly updates at runtime
    def update_password(password, password_window):
        EMAIL_CONFIG["email_password"] = password
        password_window.destroy()

    def forget_password(self):
        """
        Removes the password from the config file.
        """

        raise NotImplementedError("This feature is not yet implemented.") # TODO implement this feature (needs to be at runtime)

    def close_server(self):
        self.server.close()