
import os
from config import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from CTkMessagebox import CTkMessagebox
except ImportError:
    os.system("pip install CTkMessagebox")
    from CTkMessagebox import CTkMessagebox

class EmailHandler:
    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = "recipient_email@gmail.com"

        if not self.email_address or not self.email_password:
            raise ValueError("Email credentials not found. Please set the EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.")

    def send_bug_report(self, title, body, message_box_root_window):
        """
        Send a bug report via email.

        params:
            title (str): The title of the bug report.
            body (str): The body of the bug report.
        """
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.recipient_email
        msg['Subject'] = f"Bug Report: {title}"

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, self.recipient_email, text)
            server.quit()
            msg = CTkMessagebox(master=message_box_root_window, 
                                title="Error while sending bug report",
                                message=f"An error occurred while sending the bug report.\n{str(e)}", 
                                icon="error", 
                                options=["Close", "Retry"],
                                justify="center")
        except Exception as e:
            msg = CTkMessagebox(master=message_box_root_window, 
                                title="Error while sending bug report",
                                message=f"An error occurred while sending the bug report.\n{str(e)}", 
                                icon="error", 
                                options=["Close", "Retry"],
                                justify="center")
            
    def close():