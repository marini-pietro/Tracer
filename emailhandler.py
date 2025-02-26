import os, json
from config import EMAIL_CONFIG, VERSION, WINDOW_RESOLUTION
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

try:
    from CTkMessagebox import CTkMessagebox
    from customtkinter import CTkFrame
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    os.system("pip install -r requirements.txt")   
    from CTkMessagebox import CTkMessagebox
    from customtkinter import CTkFrame
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

class EmailHandler:
    def __init__(self):
        self.email_address = EMAIL_CONFIG["email_address"]
        self.recipient_email = "recipient_email@gmail.com"

        self.msg = MIMEMultipart()
        self.msg['From'] = self.email_address
        self.msg['To'] = self.recipient_email

        if not self.email_address:
            raise ValueError("Email address not found. Please enter a valid value.")

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
            if mode == "config-credentials":
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
        except Exception as ex:
            message_box: CTkMessagebox = CTkMessagebox(master=message_box_root_window, 
                                title="Error while sending bug report",
                                message=f"An error occurred while sending the bug report.\n{str(ex)}", 
                                icon="error", 
                                options=["Close", "Retry"],
                                justify="center")
            
    def show_report_modality_window(self, root):
        """
        Show the bug report modality window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        WINDOW_WIDTH, WINDOW_HEIGHT = int(WINDOW_RESOLUTION.split('x')[0]), int(WINDOW_RESOLUTION.split('x')[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        modality_window = CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        modality_window.pack(expand=False)
        modality_window.pack_propagate(False) # Prevent the frame from resizing to minimum size to fit its children

        # 

    def close_server(self):
        self.server.close()