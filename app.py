import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'CTkColorPicker')) # Add the CTkColorPicker module path to sys.path
del sys

try:
    import customtkinter as CTk
    from tkinter import filedialog
    from PIL import Image
    from apihandler import APIHandler
    from ydkhandler import YDKHandler
    from config import * # Import everything from config.py without having to name it every time
    from CTkColorPicker.ctk_color_picker_widget import CTkColorPicker
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix blurry text on Windows TODO look into this
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID) # Set the app id for Windows (necessary for the icon to show up in the taskbar)
    del ctypes

except ImportError as e:
    os.system("pip install -r requirements.txt") # Install the required packages
    import customtkinter as CTk
    from tkinter import filedialog
    from PIL import Image
    from apihandler import APIHandler
    from ydkhandler import YDKHandler
    from config import * # Import everything from config.py without having to name it every time
    from CTkColorPicker.ctk_color_picker_widget import CTkColorPicker
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # Fix blurry text on Windows TODO look into this
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID) # Set the app id for Windows (necessary for the icon to show up in the taskbar)
    del ctypes


# Initialize constants
resolution_split: list[str] = WINDOW_RESOLUTION.split("x")
WINDOW_WIDTH, WINDOW_HEIGHT = int(resolution_split[0]),int(resolution_split[1])

class App(CTk.CTk):
    def __init__(self):
        # Initialize the main window
        CTk.set_appearance_mode(APPEARENCE_MODE) # Set the appearance mode
        self.root = CTk.CTk() # Create the main window class
        self.root.geometry(WINDOW_RESOLUTION) # Set the window resolution
        self.root.resizable(False, False) # Disable window resizing
        self.root.grid_columnconfigure(0, weight=1) # Set the column to expand with the window
        self.root.grid_rowconfigure(0, weight=1) # Set the row to expand with the window

        # Initialize the APIHandler and YDKHandler classes
        self.api_handler = APIHandler()
        self.ydk_handler = YDKHandler(self.api_handler)

        # Set centered window title and icon
        self.root.title("Tracer") # TODO center the title string
        if os.name == "nt": # If the OS is Windows
            self.root.iconbitmap("./img/icon.ico")

        # Initial menu window
        self.main_logo_label: CTk.CTkLabel = self.create_img("./img/placeholder_icon.png", img_position=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2-150), anchor="center") # Load the main logo
        self.new_sheet_button: CTk.CTkButton = self.create_button("New Sheet", button_position=(WINDOW_WIDTH//2-50, WINDOW_HEIGHT//2+50), button_size=(100, 50), 
                          command=lambda: self.create_new_sheet(pos=(WINDOW_WIDTH//2 - (WINDOW_WIDTH*0.9)//2, WINDOW_HEIGHT//2 - (WINDOW_HEIGHT*0.9)//2), size=(WINDOW_WIDTH*0.9, WINDOW_HEIGHT*0.9)), button_color='light blue', text_color='white', corner_radius=10, hover=True) # Create the new sheet button

    def show_window(self):
        self.root.mainloop() # Start the main loop

    def create_new_sheet(self, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (100, 100)):
        """
        Creates a new sheet in the window.

        """

        # Create new subwindow
        new_window = CTk.CTkFrame(self.root, width=size[0], height=size[1])
        new_window.place(x=pos[0], y=pos[1]) # Place the subwindow

        # Create a label and entry for text input
        label = CTk.CTkLabel(new_window, text="Enter name of combo sheet:", width=size[0]*0.8, height=30)
        label.place(x=size[0]//2-label.winfo_reqwidth()//2, y=10)
        entry = CTk.CTkEntry(new_window, width=size[0]*0.8, height=50)
        entry.place(x=size[0]//2-entry.winfo_reqwidth()//2, y=60)

        # Create switches
        switch1 = CTk.CTkSwitch(new_window, text="Import cards from YDK file.")
        switch1.place(x=size[0]//2-switch1.winfo_reqwidth()//2, y=120)
        switch2 = CTk.CTkSwitch(new_window, text="Option 2")
        switch2.place(x=size[0]//2-switch2.winfo_reqwidth()//2, y=170)

        #Create color picker
        color_picker = CTkColorPicker(new_window, orientation="horizontal", initial_color="#ffffff") #TODO change color picker so the color can be changed also by writing the hex code
        color_picker.place(x=(size[0]-color_picker.winfo_reqwidth())//2-20, y=220) # TODO fix the color picker position

        # Create a button to submit the input
        submit_button = CTk.CTkButton(new_window, text="Submit", command=lambda: self.process_new_sheet_input(entry.get(), switch1.get(), switch2.get(), color_picker.get()))
        submit_button.place(x=size[0]//2-submit_button.winfo_reqwidth()//2, y=size[1]-submit_button.winfo_reqheight()-10) # Place the button at the bottom center of the window

    def process_new_sheet_input(self, text: str, switch1_state, switch2_state, color: str):
        """
        Process the input from the new sheet settings window.
        Args:
            text (str): The text input.
            switch1_state (bool): The state of switch 1.
            switch2_state (bool): The state of switch 2.
        """
        print(f"Text: {text}, Switch 1: {switch1_state}, Switch 2: {switch2_state} Color: {color}")

        if switch1_state: # If the first switch is on
            ydk_path = filedialog.askopenfilename(title="Select YDK file", filetypes=[("YDK files", "*.ydk")]) # Open the file dialog to select a ydk file     
            self.ydk_handler.read_ydk(ydk_path) # Load the ydk file

    def create_img(self, img_path: str, img_position: tuple[int, int], img_size: tuple[int, int] = None, label_text: str = '', anchor: str = 'topleft') -> CTk.CTkLabel:
        """
        Loads an places image into the window with the given path, position and size.

        Args:
            img_path (str): The path to the image file.
            img_position (tuple[int, int]): The position to place the image.
            img_size (tuple[int, int], optional): The size of the image. If None, the image size is used. Defaults to None.
            label_text (str, optional): The text to display with the image. Defaults to ''.
            anchor (str, optional): The anchor point of the image. Defaults to 'topleft'.
        
        Returns:
            CTk.CTkLabel: The label object containing the image.
        
        Raises: 
            FileNotFoundError: If the image file is not found.
            ValueError: If the image position or image size tuples are invalid.
        """

        # Check if the arguments are valid
        if not os.path.exists(img_path): raise FileNotFoundError(f"Image file not found at path: {img_path}") # Check if the image file exists
        if len(img_position) != 2: raise ValueError("Image position must be a tuple with 2 integers.") # Check if the image position is valid
        if (img_position[0] <= 0 or img_position[1] <= 0): raise ValueError("Image position must be greater than 0.") # Check if the image position is valid
        if img_size is not None and len(img_size) != 2: raise ValueError("Image size must be a tuple with 2 integers.") # Check if the image size tuple lenght is valid
        if img_size is not None and (img_size[0] <= 0 or img_size[1] <= 0): raise ValueError("Image size must be greater than 0.") # Check if the image size is valid
        if anchor not in ["topleft", "center", "bottomright", "topright", "bottomleft"]: raise ValueError("Invalid anchor point.") # Check if the anchor point is valid

        pillow_img: Image = Image.open(img_path) # Open the image with pillow
        if img_size is None: img_size = pillow_img.size # If no size is provided, use the image size
        ctk_img = CTk.CTkImage(pillow_img, size=img_size) # Load the image into ctk image class with correct arguments
        ctk_label = CTk.CTkLabel(self.root, image=ctk_img, text=label_text) # Load the image into ctk label class
        ctk_label.pack()
        match anchor:
            case "topleft":
                ctk_label.place(x=img_position[0], y=img_position[1]) # Set the image position to the top left
            case "center":
                ctk_label.place(x=img_position[0]-img_size[0]//2, y=img_position[1]-img_size[1]//2) # Set the image position to the center
            case "bottomright":
                ctk_label.place(x=img_position[0]-img_size[0], y=img_position[1]-img_size[1])
            case "topright":
                ctk_label.place(x=img_position[0]-img_size[0], y=img_position[1])
            case "bottomleft":
                ctk_label.place(x=img_position[0], y=img_position[1]-img_size[1])
        return ctk_label
    
    def create_button(self, text: str, button_position: tuple[int, int], button_size: tuple[int, int], command: callable, button_color: str = "blue", text_color: str = "white", corner_radius: int = 90, hover: bool = True, hover_color: tuple[int, int, int] = [255, 255, 255]) -> CTk.CTkButton:
        """
        Creates a button in the window with the given text, position, size and command.

        Args:
            text (str): The text to display on the button.
            button_position (tuple[int, int]): The position to place the button.
            button_size (tuple[int, int]): The size of the button.
            command (callable): The function to run when the button is clicked.
            button_color (str, optional): The color of the button. Defaults to "blue".
            text_color (str, optional): The color of the text. Defaults to "white".
            corner_radius (int, optional): The corner radius of the button. Defaults to 90.
            hover (bool, optional): If the button should change color on hover. Defaults to True.
        
        Returns:
            CTk.CTkButton: The button object.
        
        Raises:
            ValueError: If the button position or button size tuples are invalid.
        """

        # Check if the arguments are valid
        if len(button_position) != 2: raise ValueError("Button position must be a tuple with 2 integers.") # Check if the button position is valid
        if (button_position[0] <= 0 or button_position[1] <= 0): raise ValueError("Button position must be greater than 0.")
        if len(button_size) != 2: raise ValueError("Button size must be a tuple with 2 integers.")
        if (button_size[0] <= 0 or button_size[1] <= 0): raise ValueError("Button size must be greater than 0.")

        button = CTk.CTkButton(self.root, text=text, command=command, fg_color=button_color, text_color=text_color, width=button_size[0], height=button_size[1], hover=hover, corner_radius=corner_radius) # Create the button object
        button.place(x=button_position[0], y=button_position[1]) # Set the button position and size
        return button

if __name__ == "__main__":
    app = App()
    app.show_window() # Start the main window
