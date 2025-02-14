import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'CTkColorPicker')) # Add the CTkColorPicker module path to sys.path
del sys

try:
    import customtkinter as CTk
    from tkinter import filedialog, StringVar
except ImportError:
    os.system("pip install -r requirements.txt") # Install the required packages
    import customtkinter as CTk
    from tkinter import filedialog, StringVar

from config import APPEARENCE_MODE, APP_ID, WINDOW_RESOLUTION, DEFAULT_COLORS # Import everything from config.py without having to name it every time
from utils import clear_cache_button_logic, create_img, create_button # Import the necessary functions from utils.py
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix blurry text on Windows TODO look into this
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID) # Set the app id for Windows (necessary for the icon to show up in the taskbar)
from apihandler import APIHandler
from ydkparser import YDKParser
from loghandler import LogHandler
from canvashandler import CanvasHandler
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
        
        self.new_sheet_button: CTk.CTkButton = create_button(master=self,
                                                             text="New Sheet",
                                                             button_position=(WINDOW_WIDTH//2-150, WINDOW_HEIGHT//2+200),
                                                             button_size=(100, 50),
                                                             text_color='white', 
                                                             corner_radius=10, 
                                                             hover=True,
                                                             command=lambda: self.new_sheet_window(pos=(WINDOW_WIDTH//2 - (WINDOW_WIDTH*0.9)//2, WINDOW_HEIGHT//2 - (WINDOW_HEIGHT*0.9)//2), window_size=(WINDOW_WIDTH*0.9, WINDOW_HEIGHT*0.9))) # Create the new sheet button
        
        self.import_sheet_button: CTk.CTkButton = create_button(master=self,
                                                                text="Import Sheet",
                                                                button_position=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2+200),
                                                                button_size=(100, 50), 
                                                                text_color='white', 
                                                                corner_radius=10, 
                                                                hover=True,
                                                                command=self.import_sheet_dialogue) # Create the import sheet button
        
        self.clear_cache_button: CTk.CTkButton = create_button(master=self,
                                                               text="Clear Cache",
                                                               button_position=(WINDOW_WIDTH//2+150, WINDOW_HEIGHT//2+200),
                                                               button_size=(100, 50),
                                                               text_color='white', corner_radius=10, hover=True,
                                                               command=lambda: asyncio_run(self.process_clear_cache_button_press())) # Create the clear cache button
        
        if clear_cache_button_logic() == False: self.clear_cache_button.configure(state='disabled') # Run the clear cache button logic (disable the button if there is no cache)

    def new_sheet_window(self, pos: tuple[int, int] = (0, 0), window_size: tuple[int, int] = (100, 100)) -> None:
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

        # Create new subwindow
        self.new_frame = CTk.CTkFrame(master=self, width=window_size[0], height=window_size[1])
        self.new_frame.place(x=pos[0], y=pos[1]) # Place the subwindow

        # Create a label and entry for text input
        sheet_name_label = CTk.CTkLabel(self.new_frame, text="Enter name of combo sheet:", width=window_size[0]*0.8, height=30)
        sheet_name_label.place(x=window_size[0] // 2 - sheet_name_label.winfo_reqwidth() // 2, y=10)
        sheet_name_entry = CTk.CTkEntry(self.new_frame, width=window_size[0]*0.8, height=50, font=("Helvetica", 16), justify="center")
        sheet_name_entry.place(x=window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2, y=60)

        # Create switches
        import_ydk = CTk.CTkSwitch(self.new_frame, text="Import cards from YDK file")
        import_ydk.place(x=window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2, y=170)
        crop_images = CTk.CTkSwitch(self.new_frame, text="Crop card images")
        crop_images.place(x=window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2, y=210)

        #Create color picker
        color_picker = CTkColorPicker(self.new_frame, orientation="horizontal", rgb_entries=True)
        color_picker.place(x=window_size[0] - color_picker.winfo_reqwidth() - 100, y=170) # Center the color picker horizontally

        #Create entry for canvas color TODO optimize this code by writing a function similar to create_button or create_img
        canvas_color_label = CTk.CTkLabel(self.new_frame, text="Enter canvas color:")
        canvas_color_label.update_idletasks() # Update the label to get the correct dimensions
        canvas_color_label.place(x=window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2, y=250)
        canvas_color_entry = CTk.CTkEntry(self.new_frame, width=75, height=25, font=("Helvetica", 14), textvariable=StringVar(value=DEFAULT_COLORS["CANVAS"]), justify="center")
        canvas_color_entry.place(x=window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2 + canvas_color_label.winfo_reqwidth() + 5, y=250)
        create_button(master=self.new_frame, 
                      text="Get from picker", 
                      button_position=(window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2 + canvas_color_label.winfo_reqwidth() + canvas_color_entry.winfo_reqwidth() + 25, 250),
                      button_size=(100, 25), 
                      command=lambda: canvas_color_entry.configure(textvariable=StringVar(value=color_picker.get().upper())), 
                      text_color='white', 
                      corner_radius=10, 
                      hover=True, 
                      fg_color="#565656") # Create a button to get the color from the color picker

        #Create entry for arrow color TODO optimize this code by writing a function similar to create_button or create_img
        arrow_color_label = CTk.CTkLabel(self.new_frame, text="Enter arrow color:")
        arrow_color_label.update_idletasks() # Update the label to get the correct dimensions
        arrow_color_label.place(x=window_size[0]//2-sheet_name_entry.winfo_reqwidth()//2, y=290)
        arrow_color_entry = CTk.CTkEntry(self.new_frame, width=75, height=25, font=("Helvetica", 14), textvariable=StringVar(value=DEFAULT_COLORS["ARROW"]), justify="center")
        arrow_color_entry.place(x=window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2 + arrow_color_label.winfo_reqwidth() + 5, y=290)
        create_button(master=self.new_frame, 
                      text="Get from picker", 
                      button_position=(window_size[0] // 2 - sheet_name_entry.winfo_reqwidth() // 2 + arrow_color_label.winfo_reqwidth() + arrow_color_entry.winfo_reqwidth() + 25, 290),
                      button_size=(100, 25), 
                      command=lambda: arrow_color_entry.configure(textvariable=StringVar(value=color_picker.get().upper())), 
                      text_color='white', 
                      corner_radius=10, 
                      hover=True, 
                      fg_color="#565656") # Create a button to get the color from the color picker

        #Create a button to close the window
        # (assigning it to a variable is not necessary since it is not used outside of this function and can be destroyed with [child.destroy() for child in self.new_frame.winfo_children()])
        create_button(master=self.new_frame, 
                      text="Close", button_position=(window_size[0]//2-50, window_size[1]-120), 
                      button_size=(100, 50), 
                      command=self.new_frame.destroy, 
                      text_color='white', 
                      hover=True, 
                      fg_color="#565656", 
                      corner_radius=10)

        # Create a button to submit the input 
        # (assigning it to a variable is not necessary since it is not used outside of this function and can be destroyed with [child.destroy() for child in self.new_frame.winfo_children()])
        create_button(master=self.new_frame, 
                      text="Submit", button_position=(window_size[0]//2-50, window_size[1]-60), button_size=(100, 50), 
                      command=lambda: self.process_new_sheet_input(sheet_name=sheet_name_entry.get(), import_ydk=import_ydk.get(), crop_images=crop_images.get(), canvas_color=canvas_color_entry.get(), arrow_color=arrow_color_entry.get()), 
                      text_color='white', 
                      hover=True, 
                      fg_color="#565656", 
                      corner_radius=10)
        
    def process_new_sheet_input(self, sheet_name: str, import_ydk: str, crop_images: str, canvas_color: str, arrow_color: str) -> None:
        """
        Process the input from the new sheet settings window.
        
        params:
            sheet_name (str): The name of the new sheet.
            import_ydk (str): If the ydk import switch is on.
            crop_images (str): If the image crop switch is on.
            canvas_color (str): The color of the canvas.
            arrow_color (str): The color of the arrows.
        """

        # Setter functions for the canvas handler

        self.canvas_handler.set_root_window(root_window=self) # Set the root window of the canvas handler

        if crop_images: self.canvas_handler.use_cropped_images = True # Set the canvas handler to use cropped images if the switch is on

        if sheet_name != "": self.canvas_handler.sheet_name = sheet_name # If the user entered a sheet name, set the sheet name

        self.canvas_handler.set_canvas_color(color=canvas_color) # Set the canvas color
        self.canvas_handler.set_arrow_color(color=arrow_color)

        # Handle ydk import if user selected to import ydk

        if import_ydk: # If the ydk import switch is on
            ydk_path = filedialog.askopenfilename(title="Select YDK file", filetypes=[("YDK files", "*.ydk")]) # Open the file dialog to select a ydk file     
            card_ids, card_data, card_img_paths = self.ydk_parser.read_ydk(ydk_path) # Load the ydk file
            
            # Pass all the cached images file system paths to the canvas handler
            [self.canvas_handler.add_image_to_list(img_path) for img_type_paths in card_img_paths for img_path in img_type_paths]

        # Destroy the widgets in the new sheet window
        [child.destroy() for child in self.new_frame.winfo_children()] # Destroy all the widgets in the window
        self.new_frame.destroy() # Destroy the frame

        self.main_logo_label.destroy()
        self.new_sheet_button.destroy()
        self.import_sheet_button.destroy()
        self.clear_cache_button.destroy()

        # Show the canvas window
        asyncio_run(self.canvas_handler.show()) # Show the canvas window 

    def import_sheet_dialogue(self) -> None:
        """
        Opens a file dialog to import a combo sheet.
        """

        file_path = filedialog.askopenfilename(title="Select combo sheet", filetypes=[("Combo sheet files", "*.json")]) # Open the file dialog to select a combo sheet TODO: implement this feature
        # Since i decided to use generic json some validation is needed to check if the file is properly formatted

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
    app.mainloop()