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
            
    def show_email_window(self, root):
        """
        Show the email window.
        
        params:
            root (Tk): The root window of the application.
        
        returns:
            None

        raises:
            None
        """

        # New subwindow
        email_window = CTkFrame(master=root, width=300, height=150, fg_color="#2b2b2b", corner_radius=25)
        email_window.pack(expand=True)
        email_window.pack_propagate(False)

        # Password label and entry
        email_label = CTkLabel(master=email_window, 
                                  text="Enter email", 
                                  fg_color="white", 
                                  bg_color="transparent")
        email_label.pack(pady=10)

        email_entry = CTkEntry(master=email_window, 
                                  width=200, 
                                  justify="center",
                                  fg_color="#2b2b2b", 
                                  bg_color="transparent", 
                                  border_color="#4a4d50", 
                                  show="*")
        email_entry.pack(pady=10)

        # Confirm button
        confirm_button = CTkButton(master=email_window, 
                                   text="Confirm", 
                                   button_size=(100, 50), 
                                   text_color="white", 
                                   fg_color="transparent", 
                                   bg_color="transparent", 
                                   border_color="#4a4d50", 
                                   corner_radius=10, 
                                   hover=True, 
                                   command=update_email(email=email_entry.get(), email_window=email_window))
        confirm_button.pack(pady=10)
    
        # Helper function to update the password TODO figure out if this properly updates at runtime
        def update_email(email, email_window):
            EMAIL_CONFIG["email_address"] = email
            email_window.destroy()
        
    def show_password_window(self, root):
        """
        Show the password window.
        
        params:
            root (Tk): The root window of the application.

        returns:
            None

        raises:
            None
        """

        # New subwindow
        password_window = CTkFrame(master=root, width=300, height=150, fg_color="#2b2b2b", corner_radius=25)
        password_window.pack(expand=True)
        password_window.pack_propagate(False)

        # Password label and entry
        password_label = CTkLabel(master=password_window, 
                                  text="Enter password", 
                                  fg_color="white", 
                                  bg_color="transparent")
        password_label.pack(pady=10)

        password_entry = CTkEntry(master=password_window, 
                                  width=200,
                                  justify="center",
                                  fg_color="#2b2b2b", 
                                  bg_color="transparent", 
                                  border_color="#4a4d50", 
                                  show="*")
        password_entry.pack(pady=10)

        # Confirm button
        confirm_button = CTkButton(master=password_window, 
                                   text="Confirm", 
                                   button_size=(100, 50), 
                                   text_color="white", 
                                   fg_color="transparent", 
                                   bg_color="transparent", 
                                   border_color="#4a4d50", 
                                   corner_radius=10, 
                                   hover=True, 
                                   command=update_password(password=password_entry.get(), password_window=password_window))
        confirm_button.pack(pady=10)
    
        # Helper function to update the password TODO figure out if this properly updates at runtime
        def update_password(password, password_window):
            EMAIL_CONFIG["email_password"] = password
            password_window.destroy()
        
        
    def show_report_modality_window(self, root):
        """
        Show the bug report modality window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        WINDOW_WIDTH, WINDOW_HEIGHT = int(WINDOW_RESOLUTION.split('x')[0]), int(WINDOW_RESOLUTION.split('x')[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # New subwindow
        modality_window = CTkFrame(master=root, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        modality_window.pack(expand=True, anchor="center") # Pack the frame and prevent it from resizing to fit the window
        modality_window.pack_propagate(False) # Prevent the frame from resizing to minimum size to fit its children

        # Buttons to choose the mode
        report_as_issue_button: CTkButton = create_button(master=modality_window,
                                                          text="Report as github issue",
                                                          button_size=(100, 50),
                                                          text_color="white",
                                                          fg_color="transparent",
                                                          bg_color="transparent",
                                                          border_color="#4a4d50",
                                                          corner_radius=10,
                                                          should_be_placed=False,
                                                          hover=True,
                                                          command= lambda: os.system(f"start {REPO_URL}/issues/new"))
        report_as_issue_button.pack(expand=True, anchor="center")

        report_as_email_button: CTkButton = create_button(master=modality_window,
                                                          text="Report as email",
                                                          button_size=(100, 50),
                                                          text_color="white",
                                                          fg_color="transparent",
                                                          bg_color="transparent",
                                                          border_color="#4a4d50",
                                                          corner_radius=10,
                                                          should_be_placed=False,
                                                          hover=True,
                                                          command= lambda: (modality_window.destroy(), self.show_email_window(root)))  
        report_as_email_button.pack(expand=True, anchor="center")

    def show_email_window(self, root):
        """
        Show the email window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        WINDOW_WIDTH, WINDOW_HEIGHT = int(WINDOW_RESOLUTION.split('x')[0]), int(WINDOW_RESOLUTION.split('x')[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # New subwindow
        email_window = CTkFrame(master=root, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        email_window.pack(expand=True, anchor="center")
        email_window.pack_propagate(False)

        # Email label and relative entry
        email_label: CTkLabel = CTkLabel(master=email_window, 
                                        text="Email",
                                        font=("Helvetica", 16),  # Set the font and size TODO do the same for all other labels (maybe add font size to config file and settings menu)
                                        fg_color="transparent", 
                                        bg_color="transparent")
        email_entry: CTkEntry = CTkEntry(master=email_window,
                                        width=50,
                                        justify="center",
                                        fg_color="#2b2b2b",
                                        bg_color="transparent",
                                        border_color="#4a4d50")
        email_label.pack(expand=True, anchor="center")
        email_entry.pack(expand=True, anchor="center")

        # Title label and relative entry
        title_label: CTkLabel = CTkLabel(master=email_window, 
                                         text="Title", 
                                         fg_color="white", 
                                         bg_color="transparent")
        title_entry: CTkEntry = CTkEntry(master=email_window,
                                        width=50,
                                        justify="center",
                                        fg_color="#2b2b2b",
                                        bg_color="#transparent",
                                        border_color="#4a4d50")
        title_label.pack(expand=True, anchor="center")
        title_entry.pack(expand=True, anchor="center")

        # Body label and relative entry
        body_label: CTkLabel = CTkLabel(master=email_window, 
                                         text="Body", 
                                         font_size=20, 
                                         fg_color="white", 
                                         bg_color="transparent")
        body_entry: CTkEntry = CTkEntry(master=email_window,
                                        width=50,
                                        justify="center",
                                        fg_color="#2b2b2b",
                                        bg_color="#transparent",
                                        border_color="4a4d50")
        body_label.pack(expand=True, anchor="center")
        body_entry.pack(expand=True, anchor="center")

        # Send and autenthicate with google button
        google_auth_button: CTkButton = create_button(master=email_window,
                                                      text="Send and authenticate with Google",
                                                      button_size=(100, 50),
                                                      text_color="white",
                                                      fg_color="transparent",
                                                      bg_color="transparent",
                                                      border_color="#4a4d50",
                                                      corner_radius=10,
                                                      should_be_placed=False,
                                                      hover=True,
                                                      command= lambda: (email_window.destroy(), self.send_bug_report(title=title_entry.get(), body=body_entry.get(), message_box_root_window=root, mode="google-auth")))
        google_auth_button.pack(expand=True, anchor="center")

        # Send and enter password button
        send_button: CTkButton = create_button(master=email_window,
                                               text="Send and enter password",
                                               button_size=(100, 50),
                                               text_color="white",
                                               fg_color="transparent",
                                               bg_color="transparent",
                                               border_color="#4a4d50",
                                               corner_radius=10,
                                               should_be_placed=False,
                                               hover=True,
                                               command= lambda: (email_window.destroy(), self.send_bug_report(title=title_entry.get(), body=body_entry.get(), message_box_root_window=root, mode="config-credentials")))
        send_button.pack(expand=True, anchor="center")

    def forshow_password_window(self):
        """
        Removes the password from the config file.
        """

        raise NotImplementedError("This feature is not yet implemented.") # TODO implement this feature (needs to be at runtime)

    def close_server(self):
        self.server.close()