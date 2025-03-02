import os, json, config
from utils import set_config_variable
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

try:
    import customtkinter as ctk
    from CTkMessagebox import CTkMessagebox
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from tkinter import BooleanVar
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    os.system("pip install -r requirements.txt")
    import customtkinter as ctk 
    from CTkMessagebox import CTkMessagebox
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from tkinter import BooleanVar
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

class EmailHandler:
    def __init__(self, log_handler):
        self.recipient_email = config.EMAIL_CONFIG["email_recipient"]
        self.log_handler = log_handler

        self.msg = MIMEMultipart()
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
        else:
            raise ValueError("No token file found. Please authenticate again.")
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise ValueError("Invalid or expired credentials. Please authenticate again.")
        return creds

    def authenticate_user(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_955126219072-1sqqr5se4taf4p3ago6jhj6p3ipo4jki.apps.googleusercontent.com.json', 
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        return creds

    def send_bug_report(self, title, body, email, message_box_root_window, mode="config-credentials"):
        """
        Send a bug report via email.

        params:
            title (str): The title of the bug report.
            body (str): The body of the bug report.
            message_box_root_window (Tk): The root window of the application.
            mode (str): The mode of the bug report. Default is "config-credentials". Can be "config-credentials" or "google-auth".
        """
        self.msg['Subject'] = f"[Tracer Bug Report] {title} - V{config.VERSION} - {datetime.today().strftime('%Y-%m-%d')}"
        self.msg.attach(MIMEText(body, 'plain'))

        try:
            # Gather credentials and login
            if mode == "config-credentials":
                if config.EMAIL_CONFIG["email_password"] == "": 
                    password = self.show_password_window(root=message_box_root_window)
                self.server.login(email, password)
            elif mode == "google-auth":
                try:
                    self.credentials: Credentials = self.load_credentials()
                except ValueError:
                    self.credentials: Credentials = self.authenticate_user()
                self.server.login(email, self.credentials.token)

            # Send the email
            self.msg['From'] = email # Update the from email address
            text = self.msg.as_string()
            self.server.sendmail(email, self.recipient_email, text)

            # Show a success message
            message_box: CTkMessagebox = CTkMessagebox(master=message_box_root_window, 
                                title="Success",
                                message="Bug report sent successfully.",
                                icon="check", 
                                options=["Close", "Send another"],
                                justify="center")
            self.log_handler.log(message=f"Bug report sent successfully with email: {email}.", type="INFO")
        except Exception as ex:
            message_box: CTkMessagebox = CTkMessagebox(master=message_box_root_window, 
                                title="Error while sending bug report",
                                message=f"An error occurred while sending the bug report.\n{str(ex)}", 
                                icon="cancel", 
                                options=["Close", "Retry"],
                                justify="center")
            self.log_handler.log(message=f"An error occurred while sending the bug report.\n{str(ex)}", type="ERROR")

    def show_password_window(self, root):
        """
        Shows a window to enter the email password.
        """

        def submit_password():
            password = password_entry.get() # Get the password from the entry
            if remember_password_var.get(): set_config_variable("email_password", password) # Save the password if the user wants to
            password_window.destroy() # Close the window
            return password

        # Create new top level window
        password_window = ctk.CTkToplevel(root)
        password_window.title("Enter Password")

        # Create the password label
        password_label = ctk.CTkLabel(password_window, text="Please enter your email password:")

        # Create the password entry
        password_entry = ctk.CTkEntry(password_window, show="*")

        # Create the remember password checkbox
        remember_password_var = BooleanVar(value=False)
        remember_password = ctk.CTkCheckBox(password_window, text="Remember password", variable=remember_password_var)

        # Create the submit button
        submit_button = ctk.CTkButton(password_window, text="Submit", command=lambda: submit_password())

        # Pack the widgets
        password_label.pack(pady=10, anchor="center", expand=True)
        password_entry.pack(pady=5, anchor="center", expand=True)
        remember_password.pack(pady=5, anchor="center", expand=True)
        submit_button.pack(pady=10, anchor="center", expand=True)

    def forget_password(self): # TODO implement widget to do this
        """
        Removes the password from the config file.
        """

        set_config_variable(variable_name="email_password", value="")

    def close_server(self):
        self.server.close()