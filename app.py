# Import pip installed modules, if installation fails, install the required packages and retry the import
import os

# Create necessary directories if they do not exist
directories = [
    "data/card_data",
    "data/img/cache",
    "data/img/cache/cards",
    "data/img/cache/cards_cropped",
    "data/img/cache/cards_small"
]

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

try:
    from customtkinter import CTk, CTkLabel, CTkButton, CTkEntry, CTkFrame, CTkSwitch, CTkCheckBox, CTkImage, set_appearance_mode
    from CTkMessagebox import CTkMessagebox
    from PIL import Image
    from tkinter import filedialog, StringVar, BooleanVar
except ImportError:
    os.system("pip install -r requirements.txt") # Install the required packages
    from customtkinter import CTk, CTkLabel, CTkButton, CTkEntry, CTkFrame, CTkSwitch, CTkCheckBox, CTkImage, set_appearance_mode
    from CTkMessagebox import CTkMessagebox
    from PIL import Image
    from tkinter import filedialog, StringVar, BooleanVar

# Built in and code defined modules
import config
from utils import clear_cache_button_logic, set_config_variable # Import the necessary functions from utils.py
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2) # Set DPI awareness to per-monitor DPI aware
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_ID) # Set the app id for Windows (necessary for the icon to show up in the taskbar)
del ctypes
from CTkColorPicker.ctk_color_picker_widget import CTkColorPicker
from apihandler import APIHandler
from ydkparser import YDKParser
from loghandler import LogHandler
from sheethandler import SheetHandler
from emailhandler import EmailHandler
from card import Card
from CTkColorPicker.ctk_color_picker_widget import CTkColorPicker
from asyncio import run as asyncio_run

# Initialize constants
resolution_split: list[str] = config.WINDOW_RESOLUTION.split("x")
WINDOW_WIDTH, WINDOW_HEIGHT = int(resolution_split[0]),int(resolution_split[1])

class App(CTk):
    def __init__(self):
        # Initialize the main window
        set_appearance_mode(config.APPEARENCE_MODE) # Set the appearance mode
        super().__init__()  # Initialize the CTk window
        self.geometry(config.WINDOW_RESOLUTION) # Set the window resolution
        self.resizable(False, False) # Disable window resizing
        self.grid_columnconfigure(0, weight=1) # Set the column to expand with the window
        self.grid_rowconfigure(0, weight=1) # Set the row to expand with the window
        self.protocol("WM_DELETE_WINDOW", self.destroy) # Set the close button to destroy the window

        # Initialize the necessary objects
        self.log_handler = LogHandler()
        self.api_handler = APIHandler(log_handler=self.log_handler)
        self.ydk_parser = YDKParser(api_handler=self.api_handler, log_handler=self.log_handler)
        self.sheet_handler = SheetHandler(log_handler=self.log_handler, ydk_parser=self.ydk_parser, api_handler=self.api_handler, root_window=self)
        self.email_handler = EmailHandler(log_handler=self.log_handler)
        self.card_objects: dict[list[Card], list[Card], list[Card]] = {"main": [ ],
                                                                       "extra": [ ], 
                                                                       "side": [ ]} # Important: the cards should be unique, no duplicates

        # Set centered window title and icon
        self.title("Tracer")
        if os.name == "nt": # If the OS is Windows
            self.iconbitmap("./data/img/icon.ico")

        # Init main menu widgets
        pil_img = Image.open("data/img/placeholder_icon.png")
        scale = 0.75
        self.main_logo_label = CTkLabel(master=self,
                                            text="",
                                            image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                          int(pil_img.height*scale))),
                                            width=pil_img.width*scale,
                                            height=pil_img.height*scale,
                                            fg_color="transparent",
                                            bg_color="transparent"
                                )

        self.new_sheet_button = CTkButton(master=self,
                                              text="New Sheet",
                                              text_color="white",
                                              command=self.new_sheet_window,
                                              fg_color="transparent",
                                              bg_color="transparent",
                                              hover_color="#5b5b5b",
                                              border_color="#5b5b5b",
                                              border_width=2,
                                              corner_radius=10,
                                              hover=True)
        
        self.import_sheet_button = CTkButton(master=self,
                                                 text="Import Sheet",
                                                 text_color="white",
                                                 command=self.import_sheet_dialogue,
                                                 fg_color="transparent",
                                                 bg_color="transparent",
                                                 hover_color="#5b5b5b",
                                                 border_color="#5b5b5b",
                                                 border_width=2,
                                                 corner_radius=10,
                                                 hover=True)

        self.clear_cache_button = CTkButton(master=self,
                                                text="Clear Cache",
                                                text_color="white",
                                                command=lambda: asyncio_run(self.process_clear_cache_button_press()),
                                                fg_color="transparent",
                                                bg_color="transparent",
                                                hover_color="#5b5b5b",
                                                border_color="#5b5b5b",
                                                border_width=2,
                                                corner_radius=10,
                                                hover=True)

        # Technically a label but will behave like a button
        pil_img = Image.open("data/img/settings_light.png" if config.APPEARENCE_MODE == "dark" else "data/img/settings_dark.png")
        scale = 0.1
        self.settings_button = CTkLabel(master=self,
                                            text="",
                                            image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                          int(pil_img.height*scale))),
                                            width=pil_img.width*scale,
                                            height=pil_img.height*scale,
                                            fg_color="transparent",
                                            bg_color="transparent"
                                )

        if clear_cache_button_logic() == False: self.clear_cache_button.configure(state="disabled") # Run the clear cache button logic (disable the button if there is no cache)

        # Bind events
        self.settings_button.bind("<Button-1>", lambda _: (self.settings_button.unbind("<Button-1>"), self.show_settings_window(event=_))) # Bind the settings button to the function to show the settings window

        self.show_main_menu()

    def show_main_menu(self):
        """
        Initializes and shows the main menu widgets.
        """
        self.main_logo_label.place(relx=0.5, rely=0.4, anchor="center") # Place the main logo label
        self.new_sheet_button.place(relx=0.3, rely=0.8, anchor="center", y=0)
        self.import_sheet_button.place(relx=0.5, rely=0.8, anchor="center", y=0)
        self.clear_cache_button.place(relx=0.7, rely=0.8, anchor="center", y=0)
        self.settings_button.place(relx=1, rely=0, anchor="ne", x=-25, y=25) # Place the settings button with padding

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
        new_frame = CTkFrame(master=self, width=frame_width, height=frame_height, corner_radius=25, fg_color="#2b2b2b")
        new_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its children

        # Create a button to close the new sheet window
        pil_img = Image.open("data/img/cross_light.png" if config.APPEARENCE_MODE == "dark" else "data/img/cross_dark.png")
        scale = 0.15
        close_button = CTkLabel(master=new_frame,
                                    text="",
                                    image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                  int(pil_img.height*scale))),
                                    width=pil_img.width*scale,
                                    height=pil_img.height*scale,
                                    fg_color="transparent",
                                    bg_color="transparent"
                                    )   
        
        # Create a label and entry for text input
        sheet_name_label = CTkLabel(new_frame, text="Enter name of combo sheet:", width=frame_width*0.5, height=30)
        sheet_name_entry = CTkEntry(new_frame, width=frame_width*0.5, height=50, font=("Helvetica", 16), justify="center")
        
        # Create switches
        import_ydk = CTkSwitch(new_frame, 
                                   text="Import cards from YDK file",
                                   progress_color="#565656")

        # Create color picker
        color_picker = CTkColorPicker(new_frame, 
                                      orientation="horizontal", 
                                      button_color="#565656",
                                      button_hover_color="#000000",
                                      rgb_entries=True)
        
        # Create entry for canvas color
        # | Create validation function for the entries
        def validate_color_entry(action, value_if_allowed, widget_name):
            if action == '1':  # Insert
                print(len(value_if_allowed))
                if len(value_if_allowed) > 7: return False # If the new text is longer than 7 characters, refuse it
                if value_if_allowed[0] != "#": return False # If the new text does not start with a #, refuse it
                if any(char not in "0123456789ABCDEF" for char in value_if_allowed[1:].upper()): 
                    return False # If the new text is a special character or a letter after F, refuse it
                
                widget = self.nametowidget(widget_name) # TODO figure out why this is not working (the input is not being capitalized)
                widget.delete(0, 'end')  # Clear the current entry
                widget.insert(0, value_if_allowed.upper())  # Insert the capitalized text

                return True
            elif action == '0' and value_if_allowed=="":  # Delete
                return False
            
            return True # Allow everything else (focus change action)

        #  | Register the validation function
        vcmd = (self.register(validate_color_entry), '%d', '%P', '%W')

        canvas_color_frame = CTkFrame(new_frame)
        canvas_color_label = CTkLabel(canvas_color_frame, 
                                          text="Enter canvas color:")
        canvas_color_entry = CTkEntry(canvas_color_frame, 
                                      width=100, 
                                      height=25, 
                                      font=("Helvetica", 14), 
                                      textvariable=StringVar(value=config.DEFAULT_COLORS["CANVAS"]), 
                                      justify="center",
                                      validate="key",
                                      validatecommand=vcmd,
                                      corner_radius=10)
        canvas_entry_button = CTkButton(master=canvas_color_frame,
                                            text="Get from picker", 
                                            width=100,
                                            height=25,
                                            command=lambda: canvas_color_entry.configure(textvariable=StringVar(value=color_picker.get().upper())), 
                                            text_color="white", 
                                            fg_color="transparent",
                                            hover_color="#5b5b5b",
                                            border_color="#5b5b5b",
                                            border_width=2,
                                            corner_radius=10, 
                                            hover=True)
        
        # Create entry for arrow color
        arrow_color_frame = CTkFrame(master=new_frame)
        arrow_color_label = CTkLabel(master=arrow_color_frame, 
                                         text="Enter arrow color:")
        arrow_color_entry = CTkEntry(master=arrow_color_frame, 
                                     width=100, 
                                     height=25, 
                                     font=("Helvetica", 14), 
                                     textvariable=StringVar(value=config.DEFAULT_COLORS["ARROW"]), 
                                     justify="center",
                                     validate="key",
                                     validatecommand=vcmd,
                                     corner_radius=10)
        arrow_color_entry_button = CTkButton(master=arrow_color_frame,
                                                 text="Get from picker", 
                                                 width=100,
                                                 height=25,
                                                 command=lambda: arrow_color_entry.configure(textvariable=StringVar(value=color_picker.get().upper())), 
                                                 text_color="white", 
                                                 fg_color="transparent",
                                                 hover_color="#5b5b5b",
                                                 border_color="#565656",
                                                 border_width=2,
                                                 corner_radius=10, 
                                                 hover=True)

        # Create button to swap the colors
        pil_img = Image.open("data/img/swap_light.png" if config.APPEARENCE_MODE == "dark" else "data/img/swap_dark.png")
        scale = 0.1
        swap_colors_button = CTkLabel(master=new_frame,
                                          text="",
                                          image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                            int(pil_img.height*scale))),
                                          width=pil_img.width*scale,
                                          height=pil_img.height*scale,
                                          fg_color="transparent",
                                          bg_color="transparent"
                                          )
        
        # Create a button to submit the input
        submit_button = CTkButton(master=new_frame,
                                      text="Submit", 
                                      command=lambda: self.process_new_sheet_input(sheet_name=sheet_name_entry.get(), import_ydk=import_ydk.get(), canvas_color=canvas_color_entry.get(), arrow_color=arrow_color_entry.get(), new_frame=new_frame), 
                                      text_color="white", 
                                      fg_color="transparent",
                                      hover_color="#5b5b5b",
                                      hover=True, 
                                      border_color="#565656",
                                      border_width=2,
                                      corner_radius=25)

        # Bind events
        close_button.bind("<Button-1>", lambda _: ([child.destroy() for child in new_frame.winfo_children()], new_frame.destroy())) # Bind the close button to a function

        def swap_colors(event=None) -> None: # Function to swap the colors (event has to be included even if it is not used because of the bind function)
            arrow_color = arrow_color_entry.get()
            arrow_color_entry.configure(textvariable=StringVar(value=canvas_color_entry.get()))
            canvas_color_entry.configure(textvariable=StringVar(value=arrow_color))
        swap_colors_button.bind("<Button-1>", swap_colors)

        def submit_button_state_logic(event=None) -> None:
            if (arrow_color_entry.get() == canvas_color_entry.get()) or \
               (len(arrow_color_entry.get()) != 7 or len(canvas_color_entry.get()) != 7):
                submit_button.configure(state="disabled")
            elif (len(arrow_color_entry.get()) == 7 and len(canvas_color_entry.get()) == 7):
                submit_button.configure(state="normal")

        arrow_color_entry.bind("<KeyRelease>", submit_button_state_logic)
        canvas_color_entry.bind("<KeyRelease>", submit_button_state_logic)

        # Pack the widgets
        new_frame.place(relx=0.5, rely=0.5, anchor="center") # Pack the subwindow

        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        sheet_name_label.pack(pady=(10,0)) # Pack the label with padding
        sheet_name_entry.pack(pady=(10, 0)) # Pack the entry with padding (10 padding on top, 0 padding on bottom)

        import_ydk.pack(pady=20) # Pack the switch with padding

        color_picker.place(x=frame_width - 25, y=frame_height-250, anchor="e")

        canvas_color_frame.place(relx=0, rely=0.5, anchor="w", x=100, y=-25)
        canvas_color_label.pack(side="left")
        canvas_color_entry.pack(side="left", padx=(5, 10))
        canvas_entry_button.pack(side="left") # Pack the button

        arrow_color_frame.place(relx=0, rely=0.5, anchor="w", x=100, y=25)
        arrow_color_label.pack(side="left")
        arrow_color_entry.pack(side="left", padx=(5, 10))
        arrow_color_entry_button.pack(side="left") # Pack the button

        swap_colors_button.place(relx=0, rely=0.5, anchor="w", x=25, y=0)
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
        if sheet_name != "": self.sheet_handler.sheet_name = sheet_name # If the user entered a sheet name, set the sheet name

        self.log_handler.log(type="INFO", message=f"Created new sheet with name: {self.sheet_handler.sheet_name}.") # Log the creation of the new sheet

        self.sheet_handler.set_canvas_color(color=canvas_color) # Set the canvas color
        self.sheet_handler.set_arrow_color(color=arrow_color) # Set the arrow color

        # Handle ydk import if user selected to import ydk
        if import_ydk: # If the ydk import switch is on
            self.sheet_handler.import_ydk() # Import the ydk file
        else:
            self.sheet_handler.cards_empty_label.pack(pady=15, padx=15) # Show the empty label if the user did not import ydk

        # Un-place the widgets in the new sheet window
        [child.place_forget() for child in new_frame.winfo_children()] # Forget all the widgets in the window
        new_frame.place_forget() # Forget the frame
        self.settings_button.place_forget()

        self.main_logo_label.place_forget()
        self.new_sheet_button.place_forget()
        self.import_sheet_button.place_forget()
        self.clear_cache_button.place_forget()

        # Show the canvas window
        self.sheet_handler.show() # Show the canvas window 

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

        # Init widgets
        settings_frame = CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        settings_frame.pack_propagate(False) # Prevent the frame from resizing to minimum size to fit its children

        # Close button
        pil_img = Image.open("data/img/cross_light.png" if config.APPEARENCE_MODE == "dark" else "data/img/cross_dark.png")
        scale = 0.15
        close_button = CTkLabel(master=settings_frame,
                                    text="",
                                    image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                  int(pil_img.height*scale))),
                                    width=pil_img.width*scale,
                                    height=pil_img.height*scale,
                                    fg_color="transparent",
                                    bg_color="transparent"
                                    )

        # Appearance mode switch
        appearance_mode_switch = CTkSwitch(settings_frame, 
                                               text="Dark mode",
                                               progress_color="#4a4d50",
                                               onvalue="dark",
                                               offvalue="light",
                                               command= lambda: set_config_variable(variable_name="APPEARENCE_MODE", value="\"dark\"" if appearance_mode_switch.get() == "dark" else "\"light\"")) # Create the appearance mode switch
        # Set the switch to the current appearance mode
        if config.APPEARENCE_MODE == "dark": appearance_mode_switch.select() 
        else: appearance_mode_switch.deselect()

        # Use cropped images switch
        use_cropped_images_switch = CTkSwitch(settings_frame,
                                                  text="Use cropped images",
                                                  progress_color="#4a4d50",
                                                  onvalue="yes",
                                                  offvalue="no",
                                                  command=lambda: set_config_variable(variable_name="USE_CROPPED_IMAGES", value=True if use_cropped_images_switch.get() == "yes" else False)) # Create the use cropped images switch
        if config.USE_CROPPED_IMAGES: use_cropped_images_switch.select()
        else: use_cropped_images_switch.deselect()

        # Report bug button
        report_bug_button = CTkButton(master=settings_frame,
                                          text="Report a bug",
                                          command= lambda: self.show_report_modality_window(), 
                                          text_color="white", 
                                          fg_color="transparent",
                                          border_color="#4a4d50",
                                          border_width=2,
                                          corner_radius=10,
                                          hover_color="#4a4d50",
                                          hover=True)
        
        # Github link button
        pil_img = Image.open("data/img/github_light.png" if config.APPEARENCE_MODE == "dark" else "data/img/github_dark.png")
        scale = 0.1
        github_link_button = CTkLabel(master=settings_frame,
                                          text="",
                                          image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                            int(pil_img.height*scale))),
                                          width=pil_img.width*scale,
                                          height=pil_img.height*scale,
                                          fg_color="transparent",
                                          bg_color="transparent"
                                         )
        
        # Master Duel Meta link button
        pil_img = Image.open("data/img/master_duel_meta.png")
        master_duel_meta_link_button = CTkLabel(master=settings_frame,
                                                    text="",
                                                    image=CTkImage(light_image=pil_img, size=(int(pil_img.width), 
                                                                                                    int(pil_img.height))),
                                                    width=pil_img.width,
                                                    height=pil_img.height,
                                                    fg_color="transparent",
                                                    bg_color="transparent"
                                                    )
        
        # YGOProDeck link button
        pil_img = Image.open("data/img/ygoprodeck.png")
        scale = 0.25
        ygoprodeck_link_button = CTkLabel(master=settings_frame,
                                              text="",
                                              image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                                int(pil_img.height*scale))),
                                              width=pil_img.width*scale,
                                              height=pil_img.height*scale,
                                              fg_color="transparent",
                                              bg_color="transparent"
                                             )
        
        # Bind the events
        close_button.bind("<Button-1>", lambda _: (settings_frame.destroy(), self.settings_button.bind("<Button-1>", lambda _: (self.settings_button.unbind("<Button-1>"), self.show_settings_window(event=_))))) # Bind the close button to a function
        github_link_button.bind("<Button-1>", lambda _: os.system(f"start {config.REPO_URL}")) # Bind the github link button to a function
        master_duel_meta_link_button.bind("<Button-1>", lambda _: os.system("start https://www.masterduelmeta.com/"))
        ygoprodeck_link_button.bind("<Button-1>", lambda _: os.system("start https://ygoprodeck.com/"))

        # Pack the widgets
        settings_frame.place(relx=0.5, rely=0.5, anchor="center")
        close_button.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)
        appearance_mode_switch.place(relx=0.5, rely=0.5, anchor="center", y=-25) # Place the switch
        use_cropped_images_switch.place(relx=0.5, rely=0.5, anchor="center", y=25)
        report_bug_button.place(relx=0.5, rely=0.6, anchor="center", y=25)
        github_link_button.place(relx=0.4, rely=0.9, anchor="center")
        master_duel_meta_link_button.place(relx=0.5, rely=0.9, anchor="center")
        ygoprodeck_link_button.place(relx=0.6, rely=0.9, anchor="center")

    def show_report_modality_window(self):
        """
        Show the bug report modality window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        WINDOW_WIDTH, WINDOW_HEIGHT = int(config.WINDOW_RESOLUTION.split('x')[0]), int(config.WINDOW_RESOLUTION.split('x')[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # New subwindow
        modality_window = CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        modality_window.pack(expand=True, anchor="center") # Pack the frame and prevent it from resizing to fit the window
        modality_window.pack_propagate(False) # Prevent the frame from resizing to minimum size to fit its children

        # Close button
        pil_img = Image.open("data/img/cross_light.png" if config.APPEARENCE_MODE == "dark" else "data/img/cross_dark.png")
        scale = 0.15
        close_button = CTkLabel(master=modality_window,
                                    text="",
                                    image=CTkImage(light_image=pil_img, size=(int(pil_img.width*scale), 
                                                                                  int(pil_img.height*scale))),
                                    width=pil_img.width*scale,
                                    height=pil_img.height*scale,
                                    fg_color="transparent",
                                    bg_color="transparent"
                                    )
        close_button.pack(side="top", anchor="ne", padx=10, pady=10)
        close_button.bind("<Button-1>", lambda _: modality_window.destroy()) # Bind the close button to a function

        # Buttons to choose the mode
        report_as_issue_button = CTkButton(master=modality_window,
                                               text="Report as github issue",
                                               text_color="white",
                                               fg_color="transparent",
                                               bg_color="transparent",
                                               border_color="#4a4d50",
                                               border_width=2,
                                               corner_radius=10,
                                               hover=True,
                                               command= lambda: os.system(f"start {config.REPO_URL}/issues/new")) # Open the github issues page
        report_as_email_button = CTkButton(master=modality_window,
                                               text="Report as email",
                                               text_color="white",
                                               fg_color="transparent",
                                               bg_color="transparent",
                                               border_color="#4a4d50",
                                               border_width=2,
                                               corner_radius=10,
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
        password_window = CTkFrame(master=self, width=300, height=150, fg_color="#2b2b2b", corner_radius=25)
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
                                   command=self.email_handler.update_password(password=password_entry.get(), password_window=password_window))
        confirm_button.pack(pady=10)

    def show_email_compilation_window(self, root):
        """
        Show the email window.
        """

        # WINDOW_WIDTH, WINDOW_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight() # TODO figure out which is better
        window_res = config.WINDOW_RESOLUTION.split('x')
        WINDOW_WIDTH, WINDOW_HEIGHT = int(window_res[0]), int(window_res[1])
        frame_width, frame_height = WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.8

        # New subwindow
        email_window = CTkFrame(master=self, width=frame_width, height=frame_height, fg_color="#2b2b2b", corner_radius=25)
        email_window.pack(expand=True, anchor="center")
        email_window.pack_propagate(False)

        # Email label and relative entry
        email_label: CTkLabel = CTkLabel(master=email_window, 
                                                 text="Email",
                                                 font=("Helvetica", 16),  # Set the font and size TODO do the same for all other labels (maybe add font size to config file and settings menu)
                                                 fg_color="transparent", 
                                                 bg_color="transparent")
        email_entry: CTkEntry = CTkEntry(master=email_window,
                                                 width=250,
                                                 justify="center",
                                                 fg_color="#2b2b2b",
                                                 bg_color="transparent",
                                                 border_width=2,
                                                 border_color="#4a4d50")
        
        # Title label and relative entry
        title_label: CTkLabel = CTkLabel(master=email_window, 
                                                text="Title", 
                                                font=("Helvetica", 16),
                                                fg_color="transparent", 
                                                bg_color="transparent")
        title_entry: CTkEntry = CTkEntry(master=email_window,
                                                 width=250,
                                                 justify="center",
                                                 fg_color="#2b2b2b",
                                                 bg_color="transparent",
                                                 border_width=2,
                                                 border_color="#4a4d50")
        if config.EMAIL_CONFIG["email_address"] != "": email_entry.insert(0, config.EMAIL_CONFIG["email_address"]) # If the email address is already set, insert it into the entry

        # Body label and relative entry
        body_label: CTkLabel = CTkLabel(master=email_window, 
                                                text="Body", 
                                                font=("Helvetica", 16),
                                                fg_color="transparent", 
                                                bg_color="transparent")
        body_entry: CTkEntry = CTk.CTkTextbox(master=email_window,
                                                  width=450,
                                                  height=200,
                                                  fg_color="#2b2b2b",
                                                  bg_color="transparent",
                                                  border_width=2,
                                                  border_color="#4a4d50")

        # Checkbox to remember the email address
        remember_email: BooleanVar = BooleanVar(value=False)
        remember_email_checkbox: CTkCheckBox = CTkCheckBox(master=email_window,
                                                                   text="Remember email address",
                                                                   fg_color="white",
                                                                   bg_color="transparent",
                                                                   corner_radius=10,
                                                                   hover=True,
                                                                   variable=remember_email) # Set the remember email variable to true if the checkbox is checked

        # Send and autenthicate with google button
        google_auth_button = CTkButton(master=email_window,
                                           text="Send and authenticate with Google",
                                           text_color="white",
                                           fg_color="transparent",
                                           bg_color="transparent",
                                           border_color="#4a4d50",
                                           border_width=2,
                                           corner_radius=10,
                                           hover=True,
                                           command=lambda: (self.show_email_warning_messagebox(title=title_entry.get(), 
                                                                                               email=email_entry.get(),
                                                                                               body=body_entry.get("1.0", "end-1c"),
                                                                                               mode="google-auth"),
                                                            email_window.destroy(),
                                                            set_config_variable(variable_name="email_address", value="\""+ email_entry.get()+"\"") if remember_email else None))
                                           
        # Send and enter password button
        send_button = CTkButton(master=email_window,
                                    text="Send and enter password",
                                    text_color="white",
                                    fg_color="transparent",
                                    bg_color="transparent",
                                    border_color="#4a4d50",
                                    border_width=2,
                                    corner_radius=10,
                                    hover=True,
                                    command= lambda: (self.show_email_warning_messagebox(title=title_entry.get(), 
                                                                                         email=email_entry.get(),
                                                                                         body=body_entry.get(), 
                                                                                         mode="config-credentials"),
                                                      email_window.destroy(),
                                                      set_config_variable(variable_name="email_address", value="\""+email_entry.get()+"\"") if remember_email else None))

        # Pack the widgets
        email_label.pack(pady=(10, 5), anchor="center", expand=True)
        email_entry.pack(pady=(5, 10), anchor="center", expand=True)

        title_label.pack(pady=(10, 5), anchor="center", expand=True)
        title_entry.pack(pady=(5, 10), anchor="center", expand=True)

        body_label.pack(pady=(10, 5), anchor="center", expand=True)
        body_entry.pack(pady=(5, 10), anchor="center", expand=True)

        remember_email_checkbox.pack(pady=(10, 5), anchor="center", expand=True)

        google_auth_button.pack(pady=(10, 5), anchor="center", expand=True)
        send_button.pack(pady=(5, 10), anchor="center", expand=True)

    def show_email_warning_messagebox(self, title: str, email: str, body: str, mode: str) -> None:
        """
        Show a messagebox warning the user that the email might not arrive because of google authentication free tier API limits or that the authentication process might not be available because of google free tier API limits.
        
        params:
            type (str): The type of the warning message. Can be "config-credentials" or "google-auth".
            title (str): The title of the bug report.
            email (str): The email address of the user.
            body (str): The body of the bug report.
            message_box_root_window (Tk): The root window of the application.
        raises:
            None
        returns:
            None
        """

        if mode not in ["config-credentials", "google-auth"]: raise ValueError(f"Invalid mode value: {mode}. Must be google-auth or config-credentials.")
        if mode == "config-credentials":
            message = "The email might not arrive because of google authentication free tier API limits.\nIf so, please try again later or submit the bug report as an issue on github."
        elif mode == "google-auth":
            message = "The authentication process might not be available because of google free tier API limits.\nIf so, please try again later or submit the bug report as an issue on github."
        message_box: CTkMessagebox = CTkMessagebox(master=self, 
                                                   title="Warning",
                                                   message=message,
                                                   icon="warning", 
                                                   options=["Close"],
                                                   justify="center")
        
        if message_box.get() == "Close": 
            message_box.destroy()
            self.email_handler.send_bug_report(title=title, 
                                               email=email,
                                               body=body, 
                                               message_box_root_window=self, 
                                               mode=mode)

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
        self.clear_cache_button.configure(state="disabled") # Disable the clear cache button

if __name__ == "__main__":
    app = App()
    app.ydk_parser.set_app_reference(app) # Set the app reference in the ydk parser
    app.sheet_handler.set_app_reference(app) # Set the app reference in the sheet handler
    app.mainloop()