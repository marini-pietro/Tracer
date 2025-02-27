import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'CTkColorPicker')) # Add the CTkColorPicker module path to sys.path to allow importing the module TODO find a better way to do this
del sys

# Import pip installed modules, if installation fails, install the required packages and retry the import
try:
    import customtkinter as CTk
    from tkinter import filedialog, StringVar
except ImportError:
    os.system("pip install -r requirements.txt") # Install the required packages
    import customtkinter as CTk
    from tkinter import filedialog, StringVar

# Built in and code defined modules
from config import APPEARENCE_MODE, APP_ID, WINDOW_RESOLUTION, DEFAULT_COLORS, REPO_URL, USE_CROPPED_IMAGES, EMAIL_CONFIG
from utils import clear_cache_button_logic, create_img, create_button # Import the necessary functions from utils.py
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix blurry text on Windows TODO look into this
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID) # Set the app id for Windows (necessary for the icon to show up in the taskbar)
del ctypes
from apihandler import APIHandler
from ydkparser import YDKParser
from loghandler import LogHandler
from canvashandler import CanvasHandler
from emailhandler import EmailHandler
from card import Card
from CTkColorPicker.ctk_color_picker_widget import CTkColorPicker
from asyncio import run as asyncio_run

# Initialize constants
resolution_split: list[str] = WINDOW_RESOLUTION.split("x")
WINDOW_WIDTH, WINDOW_HEIGHT = int(resolution_split[0]),int(resolution_split[1])

class App(CTk.CTk):
    def __init__(self):
        # Initialize the main window
        CTk.set_appearance_mode(APPEARENCE_MODE) # Set the appearance mode
        super().__init__()  # Initialize the CTk window
        self.geometry(WINDOW_RESOLUTION) # Set the window resolution
        self.resizable(False, False) # Disable window resizing
        self.grid_columnconfigure(0, weight=1) # Set the column to expand with the window
        self.grid_rowconfigure(0, weight=1) # Set the row to expand with the window
        self.protocol("WM_DELETE_WINDOW", self.destroy) # Set the close button to destroy the window

        # Initialize the necessary objects
        self.log_handler = LogHandler()
        self.api_handler = APIHandler(log_handler=self.log_handler)
        self.ydk_parser = YDKParser(api_handler=self.api_handler, log_handler=self.log_handler)
        self.canvas_handler = CanvasHandler(log_handler=self.log_handler, ydk_parser=self.ydk_parser, api_handler=self.api_handler)
        self.email_handler = EmailHandler(log_handler=self.log_handler)
        self.card_objects: list[list[Card], list[Card], list[Card]] = [[ ], [ ], [ ]] # List containing the card objects to be displayed on the canvas

        # Set centered window title and icon
        self.title("Tracer") # TODO center the title string
        if os.name == "nt": # If the OS is Windows
            self.iconbitmap("./data/img/icon.ico")

        # Initial menu window widgets
        self.main_logo_label: CTk.CTkLabel = create_img(master=self, 
                                                        img_path="data/img/placeholder_icon.png", 
                                                        img_position=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100), 
                                                        anchor="center", 
                                                        scale=0.75) # Load the main logo
        
        self.new_sheet_button: CTk.CTkButton = create_button(
            master=self,
            text="New Sheet",
            button_position=(WINDOW_WIDTH//2-150, WINDOW_HEIGHT//2+200),
            button_size=(100, 50),
            text_color='white', 
            fg_color="transparent",
            border_color='#5b5b5b',
            border_width=2,  # Set the border width
            corner_radius=10, 
            hover=True,
            command=self.new_sheet_window # Bind the new sheet button to the function to create a new sheet
        )
        
        self.import_sheet_button: CTk.CTkButton = create_button(
            master=self,
            text="Import Sheet",
            button_position=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2+200),
            button_size=(100, 50), 
            text_color='white', 
            fg_color="transparent",
            border_color='#5b5b5b',
            border_width=2,  # Set the border width
            corner_radius=10, 
            hover=True,
            command=self.import_sheet_dialogue 
        )
        
        self.clear_cache_button: CTk.CTkButton = create_button(
            master=self,
            text="Clear Cache",
            button_position=(WINDOW_WIDTH//2+150, WINDOW_HEIGHT//2+200),
            button_size=(100, 50),
            fg_color="transparent",
            text_color='white', 
            border_color='#5b5b5b',
            border_width=2,  # Set the border width
            corner_radius=10,
            hover=True,
            command=lambda: asyncio_run(self.process_clear_cache_button_press())
        )

        # Technically a label but will behave like a button (using a label do not add code to the create_button function that will be used almost never)
        self.settings_button: CTk.CTkLabel = create_img(master=self,
                                                        img_path="data/img/settings_light.png" if APPEARENCE_MODE == "dark" else "data/img/settings_dark.png",
                                                        img_position=(WINDOW_WIDTH-50, 50),
                                                        anchor="center",
                                                        scale=0.1) # Load the settings button
        self.settings_button.bind("<Button-1>", lambda _: (self.settings_button.unbind("<Button-1>"), self.show_settings_window(event=_))) # Bind the settings button to the function to show the settings window

        if clear_cache_button_logic() == False: self.clear_cache_button.configure(state='disabled') # Run the clear cache button logic (disable the button if there is no cache)

    # Main menu submenus
    def new_sheet_window(self) -> None:
        """
        Creates a new sheet in the window.

        params:
            pos (tuple[int, int]): The position of the new sheet.
            size (tuple[int, int]): The size of the new sheet

        raises:
            ValueError: If the position or size tuples are invalid

        returns:
            None
        """

        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # Create new subwindow
        new_frame = CTk.CTkFrame(master=self, width=frame_width, height=frame_height, corner_radius=25, fg_color="#2b2b2b")
        new_frame.place(relx=0.5, rely=0.5, anchor="center") # Pack the subwindow
        new_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its children

        # Create a button to close the new sheet window
        close_button = create_img(master=new_frame,
                                  img_path="data/img/cross_light.png" if APPEARENCE_MODE == "dark" else "data/img/cross_dark.png",
                                  should_be_placed=False,
                                  scale=0.15) # Load the close button
        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        close_button.bind("<Button-1>", lambda _: ([child.destroy() for child in new_frame.winfo_children()], new_frame.destroy())) # Bind the close button to a function

        # Create a label and entry for text input
        sheet_name_label = CTk.CTkLabel(new_frame, text="Enter name of combo sheet:", width=frame_width*0.5, height=30)
        sheet_name_entry = CTk.CTkEntry(new_frame, width=frame_width*0.5, height=50, font=("Helvetica", 16), justify="center")
        sheet_name_label.pack(pady=(10,0)) # Pack the label with padding
        sheet_name_entry.pack(pady=(10, 0)) # Pack the entry with padding (10 padding on top, 0 padding on bottom)

        # Create switches
        import_ydk = CTk.CTkSwitch(new_frame, 
                                   text="Import cards from YDK file",
                                   progress_color="#565656")
        import_ydk.pack(pady=20) # Pack the switch with padding

        # Create color picker
        color_picker = CTkColorPicker(new_frame, 
                                      orientation="horizontal", 
                                      button_color="#565656",
                                      button_hover_color="#000000",
                                      rgb_entries=True)
        color_picker.place(x=frame_width - 25, y=frame_height-250, anchor="e")

        # Create entry for canvas color
        canvas_color_frame = CTk.CTkFrame(new_frame)
        canvas_color_label = CTk.CTkLabel(canvas_color_frame, 
                                          text="Enter canvas color:")
        canvas_color_entry = CTk.CTkEntry(canvas_color_frame, 
                                          width=100, 
                                          height=25, 
                                          font=("Helvetica", 14), 
                                          textvariable=StringVar(value=DEFAULT_COLORS["CANVAS"]), 
                                          justify="center",
                                          corner_radius=10)
        canvas_entry_button = create_button(master=canvas_color_frame, 
                                            text="Get from picker", 
                                            button_size=(100, 25), 
                                            command=lambda: canvas_color_entry.configure(textvariable=StringVar(value=color_picker.get().upper())), 
                                            text_color='white', 
                                            fg_color="transparent",
                                            border_color='#565656',
                                            corner_radius=10, 
                                            should_be_placed=False,
                                            hover=True)
        
        canvas_color_frame.place(relx=0, rely=0.5, anchor="w", x=100, y=-25)
        canvas_color_label.pack(side="left")
        canvas_color_entry.pack(side="left", padx=(5, 10))
        canvas_entry_button.pack(side="left") # Pack the button

        # Create entry for arrow color
        arrow_color_frame = CTk.CTkFrame(master=new_frame)
        arrow_color_label = CTk.CTkLabel(master=arrow_color_frame, 
                                         text="Enter arrow color:")
        arrow_color_entry = CTk.CTkEntry(master=arrow_color_frame, 
                                         width=100, 
                                         height=25, 
                                         font=("Helvetica", 14), 
                                         textvariable=StringVar(value=DEFAULT_COLORS["ARROW"]), 
                                         justify="center",
                                         corner_radius=10)
        arrow_color_entry_button = create_button(master=arrow_color_frame, 
                                                 text="Get from picker", 
                                                 button_size=(100, 25), 
                                                 command=lambda: arrow_color_entry.configure(textvariable=StringVar(value=color_picker.get().upper())), 
                                                 text_color='white', 
                                                 fg_color="transparent",
                                                 border_color='#565656',
                                                 corner_radius=10, 
                                                 should_be_placed=False,
                                                 hover=True)
        arrow_color_frame.place(relx=0, rely=0.5, anchor="w", x=100, y=25)
        arrow_color_label.pack(side="left")
        arrow_color_entry.pack(side="left", padx=(5, 10))
        arrow_color_entry_button.pack(side="left") # Pack the button

        # Create button to swap the colors
        swap_colors_button = create_img(master=new_frame,
                                        img_path="data/img/swap_light.png" if APPEARENCE_MODE == "dark" else "data/img/swap_dark.png",
                                        should_be_placed=False,
                                        scale=0.1)
        swap_colors_button.place(relx=0, rely=0.5, anchor="w", x=25, y=0)
        swap_colors_button.bind("<Button-1>", lambda _: self.swap_colors(arrow_color_entry, canvas_color_entry))

        # Create a button to submit the input
        submit_button = create_button(master=new_frame, 
                                      text="Submit", 
                                      button_size=(100, 50), 
                                      command=lambda: self.process_new_sheet_input(sheet_name=sheet_name_entry.get(), import_ydk=import_ydk.get(), canvas_color=canvas_color_entry.get(), arrow_color=arrow_color_entry.get(), new_frame=new_frame), 
                                      text_color='white', 
                                      fg_color="transparent",
                                      hover=True, 
                                      border_color='#565656',
                                      should_be_placed=False,
                                      corner_radius=25)
        submit_button.place(relx=0.5, rely=1.0, anchor="center", y=-15 - submit_button.winfo_reqheight()) # Place the submit button

    def process_new_sheet_input(self, sheet_name: str, import_ydk: str, canvas_color: str, arrow_color: str, new_frame) -> None:
        """
        Process the input from the new sheet settings window.
        This includes setting the canvas color, arrow color, importing ydk, packing the images and cropping images.
        
        params:
            sheet_name (str): The name of the new sheet.
            import_ydk (str): If the ydk import switch is on.
            canvas_color (str): The color of the canvas.
            arrow_color (str): The color of the arrows.
            new_frame (CTkFrame): The frame of the new sheet settings window.
        """

        # Setter functions for the canvas handler

        self.canvas_handler.set_root_window(root_window=self) # Set the root window of the canvas handler

        if sheet_name != "": self.canvas_handler.sheet_name = sheet_name # If the user entered a sheet name, set the sheet name

        self.canvas_handler.set_canvas_color(color=canvas_color) # Set the canvas color
        self.canvas_handler.set_arrow_color(color=arrow_color)

        # Handle ydk import if user selected to import ydk
        if import_ydk: # If the ydk import switch is on
            ydk_path = filedialog.askopenfilename(title="Select YDK file", filetypes=[("YDK files", "*.ydk")]) # Open the file dialog to select a ydk file     
            self.ydk_parser.read_ydk(ydk_path) # Read the ydk file, cache the data and create and store the card objects into the card_objects list

            for size in ["small", "medium", "large"]: # TODO figure out why the images do not appear in cards tab
                for card in self.card_objects[["small", "medium", "large"].index(size)]:
                    card.images[size].pack()

        else:
            self.canvas_handler.cards_empty_label.pack() # Show the empty label if the user did not import ydk

        # Destroy the widgets in the new sheet window
        [child.destroy() for child in new_frame.winfo_children()] # Destroy all the widgets in the window
        new_frame.destroy() # Destroy the frame
        self.settings_button.destroy()

        self.main_logo_label.destroy()
        self.new_sheet_button.destroy()
        self.import_sheet_button.destroy()
        self.clear_cache_button.destroy()

        # Show the canvas window
        asyncio_run(self.canvas_handler.show()) # Show the canvas window 

    def import_sheet_dialogue(self) -> None:
        """
        Opens a file dialog to import a combo sheet.

        params:
            None
        raises:
            None
        returns:
            None
        """

        file_path = filedialog.askopenfilename(title="Select combo sheet", filetypes=[("Combo sheet files", "*.json")]) # Open the file dialog to select a combo sheet TODO: implement this feature
        # Since i decided to use generic json some validation is needed to check if the file is properly formatted

    # Settings menu and subwindows
    def show_settings_window(self, event) -> None:
        """
        Shows the settings window.

        params:
            event (Event): The event that triggered the function. (Unused)
        raises:
            None
        returns:    
            None
        """

        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # Create new subwindow
        settings_frame = CTk.CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        settings_frame.place(relx=0.5, rely=0.5, anchor="center")
        settings_frame.pack_propagate(False) # Prevent the frame from resizing to minimum size to fit its children

        # Close button
        close_button: CTk.CTkLabel = create_img(master=settings_frame,
                                                img_path="data/img/cross_light.png" if APPEARENCE_MODE == "dark" else "data/img/cross_dark.png",
                                                should_be_placed=False,
                                                scale=0.15) # Load the close button
        close_button.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)
        close_button.bind("<Button-1>", lambda _: (settings_frame.destroy(), self.settings_button.bind("<Button-1>", lambda _: (self.settings_button.unbind("<Button-1>"), self.show_settings_window(event=_))))) # Bind the close button to a function

        # Appearance mode switch
        appearance_mode_switch = CTk.CTkSwitch(settings_frame, 
                                               text="Dark mode",
                                               progress_color="#4a4d50") # Create the appearance mode switch
        if APPEARENCE_MODE == "dark": appearance_mode_switch.select()  # Set the switch to the current appearance mode
        else: appearance_mode_switch.deselect()
        appearance_mode_switch.place(relx=0.5, rely=0.5, anchor="center", y=-25) # Place the switch

        # Report bug button
        report_bug_button = create_button(master=settings_frame,
                                          text="Report a bug",
                                          button_size=(100, 50),
                                          command= lambda: self.show_report_modality_window(root=self), 
                                          text_color='white', 
                                          fg_color="transparent",
                                          border_color='#4a4d50',
                                          corner_radius=10,
                                          should_be_placed=False,
                                          hover=True)
        report_bug_button.place(relx=0.5, rely=0.6, anchor="center", y=25)

        # Use cropped images switch
        use_cropped_images_switch = CTk.CTkSwitch(settings_frame,
                                                  text="Use cropped images",
                                                  progress_color="#4a4d50",
                                                  command=lambda: self.set_use_cropped_images(use_cropped_images_switch.get()))
        if USE_CROPPED_IMAGES: use_cropped_images_switch.select()
        else: use_cropped_images_switch.deselect()
        use_cropped_images_switch.place(relx=0.5, rely=0.5, anchor="center", y=25)
        
        # Github link button
        github_link_button = create_img(master=settings_frame,
                img_path="data/img/github_light.png" if APPEARENCE_MODE == "dark" else "data/img/github_dark.png",
                should_be_placed=False,
                scale=0.1) # Load the github link button
        github_link_button.place(relx=0.4, rely=0.9, anchor="center")
        github_link_button.bind("<Button-1>", lambda _: os.system(f"start {REPO_URL}")) # Bind the github link button to a function

        # Master Duel Meta link button
        master_duel_meta_link_button = create_img(master=settings_frame,
                                       img_path="data/img/master_duel_meta.png",
                                       should_be_placed=False,
                                       scale=1.0)
        master_duel_meta_link_button.place(relx=0.5, rely=0.9, anchor="center")
        master_duel_meta_link_button.bind("<Button-1>", lambda _: os.system("start https://www.masterduelmeta.com/"))

        # YGOProDeck link button
        ygoprodeck_link_button = create_img(master=settings_frame,
                    img_path="data/img/ygoprodeck.png",
                    should_be_placed=False,
                    scale=0.25)
        ygoprodeck_link_button.place(relx=0.6, rely=0.9, anchor="center")
        ygoprodeck_link_button.bind("<Button-1>", lambda _: os.system("start https://ygoprodeck.com/"))

    def show_report_modality_window(self):
        """
        Show the bug report modality window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        WINDOW_WIDTH, WINDOW_HEIGHT = int(WINDOW_RESOLUTION.split('x')[0]), int(WINDOW_RESOLUTION.split('x')[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # New subwindow
        modality_window = CTk.CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        modality_window.pack(expand=True, anchor="center") # Pack the frame and prevent it from resizing to fit the window
        modality_window.pack_propagate(False) # Prevent the frame from resizing to minimum size to fit its children

        # Close button
        close_button: CTk.CTkLabel = create_img(master=modality_window,
                                                img_path="data/img/cross_light.png" if APPEARENCE_MODE == "dark" else "data/img/cross_dark.png",
                                                should_be_placed=False,
                                                scale=0.15) # Load the close button
        close_button.pack(side="top", anchor="ne", padx=10, pady=10)
        close_button.bind("<Button-1>", lambda _: modality_window.destroy()) # Bind the close button to a function

        # Buttons to choose the mode
        report_as_issue_button: CTk.CTkButton = create_button(master=modality_window,
                                                              text="Report as github issue",
                                                              button_size=(100, 50),
                                                              text_color="white",
                                                              fg_color="transparent",
                                                              bg_color="transparent",
                                                              border_color="#4a4d50",
                                                              corner_radius=10,
                                                              should_be_placed=False,
                                                              hover=True,
                                                              command= lambda: os.system(f"start {REPO_URL}/issues/new")) # Open the github issues page
        report_as_email_button: CTk.CTkButton = create_button(master=modality_window,
                                                              text="Report as email",
                                                              button_size=(100, 50),
                                                              text_color="white",
                                                              fg_color="transparent",
                                                              bg_color="transparent",
                                                              border_color="#4a4d50",
                                                              corner_radius=10,
                                                              should_be_placed=False,
                                                              hover=True,
                                                              command= lambda: (modality_window.destroy(), self.show_email_compilation_window(root=self))) # Show the email compilation window
        
        report_as_issue_button.pack(side="left", expand=True, padx=(0, 5)) # Pack the report as issue button with padding
        report_as_email_button.pack(side="left", expand=True, padx=(5, 0)) # Pack the report as email button with padding
        
    def show_password_input_window(self):
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
        password_window = CTk.CTkFrame(master=self, width=300, height=150, fg_color="#2b2b2b", corner_radius=25)
        password_window.pack(expand=True)
        password_window.pack_propagate(False)

        # Password label and entry
        password_label = CTk.CTkLabel(master=password_window, 
                                  text="Enter password", 
                                  fg_color="white", 
                                  bg_color="transparent")
        password_label.pack(pady=10)

        password_entry = CTk.CTkEntry(master=password_window, 
                                  width=200,
                                  justify="center",
                                  fg_color="#2b2b2b", 
                                  bg_color="transparent", 
                                  border_color="#4a4d50", 
                                  show="*")
        password_entry.pack(pady=10)

        # Confirm button
        confirm_button = CTk.CTkButton(master=password_window, 
                                   text="Confirm", 
                                   button_size=(100, 50), 
                                   text_color="white", 
                                   fg_color="transparent", 
                                   bg_color="transparent", 
                                   border_color="#4a4d50", 
                                   corner_radius=10, 
                                   hover=True, 
                                   command=self.email_handler.update_password(password=password_entry.get(), password_window=password_window))
        confirm_button.pack(pady=10)

    def show_email_compilation_window(self, root):
        """
        Show the email window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        window_res = WINDOW_RESOLUTION.split('x')
        WINDOW_WIDTH, WINDOW_HEIGHT = int(window_res[0]), int(window_res[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # New subwindow
        email_window = CTk.CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        email_window.pack(expand=True, anchor="center")
        email_window.pack_propagate(False)

        # Email label and relative entry
        email_label: CTk.CTkLabel = CTk.CTkLabel(master=email_window, 
                                                 text="Email",
                                                 font=("Helvetica", 16),  # Set the font and size TODO do the same for all other labels (maybe add font size to config file and settings menu)
                                                 fg_color="transparent", 
                                                 bg_color="transparent")
        email_entry: CTk.CTkEntry = CTk.CTkEntry(master=email_window,
                                                 width=50,
                                                 justify="center",
                                                 fg_color="#2b2b2b",
                                                 bg_color="transparent",
                                                 border_width=2,
                                                 border_color="#4a4d50")
        
        # Title label and relative entry
        title_label: CTk.CTkLabel = CTk.CTkLabel(master=email_window, 
                                                text="Title", 
                                                fg_color="transparent", 
                                                bg_color="transparent")
        title_entry: CTk.CTkEntry = CTk.CTkEntry(master=email_window,
                                                 width=50,
                                                 justify="center",
                                                 fg_color="#2b2b2b",
                                                 bg_color="transparent",
                                                 border_width=2,
                                                 border_color="#4a4d50")

        # Body label and relative entry
        body_label: CTk.CTkLabel = CTk.CTkLabel(master=email_window, 
                                                text="Body", 
                                                font=("Helvetica", 16),
                                                fg_color="transparent", 
                                                bg_color="transparent")
        body_entry: CTk.CTkEntry = CTk.CTkTextbox(master=email_window,
                                                  width=450,
                                                  height=300,
                                                  fg_color="#2b2b2b",
                                                  bg_color="transparent",
                                                  border_width=2,
                                                  border_color="#4a4d50")

        # Send and autenthicate with google button
        google_auth_button: CTk.CTkButton = create_button(master=email_window,
                                                          text="Send and authenticate with Google",
                                                          button_size=(100, 50),
                                                          text_color="white",
                                                          fg_color="transparent",
                                                          bg_color="transparent",
                                                          border_width=2,
                                                          border_color="#4a4d50",
                                                          corner_radius=10,
                                                          should_be_placed=False,
                                                          hover=True,
                                                          command= lambda: (email_window.destroy(), self.email_handler.send_bug_report(title=title_entry.get(), body=body_entry.get(), message_box_root_window=root, mode="google-auth")))

        # Send and enter password button
        send_button: CTk.CTkButton = create_button(master=email_window,
                                                   text="Send and enter password",
                                                   button_size=(100, 50),
                                                   text_color="white",
                                                   fg_color="transparent",
                                                   bg_color="transparent",
                                                   border_color="#4a4d50",
                                                   corner_radius=10,
                                                   should_be_placed=False,
                                                   hover=True,
                                                   command= lambda: (email_window.destroy(), self.email_handler.send_bug_report(title=title_entry.get(), body=body_entry.get(), message_box_root_window=root, mode="config-credentials")))
        
        # Pack the widgets
        email_label.pack(expand=True, anchor="center")
        email_entry.pack(expand=True, anchor="center")

        title_label.pack(expand=True, anchor="center")
        title_entry.pack(expand=True, anchor="center")

        body_label.pack(expand=True, anchor="center")
        body_entry.pack(expand=True, anchor="center")

        google_auth_button.pack(expand=True, anchor="center")

        send_button.pack(expand=True, anchor="center")

    # Setter functions
    def set_use_cropped_images(value: bool) -> None:
        """
        Set the use cropped images variable in the ydk parser.

        params:
            use_cropped_images_switch (str): The state of the switch.
        raises:
            None
        returns:
            None
        """
        
        # Read the current contents of config.py
        with open("config.py", "r") as file:
            lines = file.readlines()
        
        # Modify the value of ASK_YDK_IMPORT_CONFIRMATION
        for i, line in enumerate(lines):
            if line.startswith("USE_CROPPED_IMAGES"):
                lines[i] = f"USE_CROPPED_IMAGES = {value}\n"
                break
        
        # Write the updated contents back to config.py
        with open("config.py", "w") as file:
            file.writelines(lines)

    def swap_colors(self, arrow_color_entry, canvas_color_entry):
        arrow_color = arrow_color_entry.get()
        arrow_color_entry.configure(textvariable=StringVar(value=canvas_color_entry.get()))
        canvas_color_entry.configure(textvariable=StringVar(value=arrow_color))

    # Helper functions

    async def process_clear_cache_button_press(self) -> None:
        """
        Clears all the cache and then disables the clear cache button.

        params:
            None
        raises:
            None
        returns:
            None
        """

        await self.ydk_parser.clear_cache() # Clear the cache
        self.clear_cache_button.configure(state='disabled') # Disable the clear cache button

if __name__ == "__main__":
    app = App()
    app.ydk_parser.set_app_reference(app) # Set the app reference in the ydk parser
    app.mainloop()