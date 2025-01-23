try:
    import os
    import customtkinter as CTk
    from PIL import Image
    from apihandler import APIHandler
    from ydkhandler import YDKHandler
    from config import * # Import everything from config.py without having to name it every time
except ImportError as e:
    import os 
    os.system("pip install -r requirements.txt") # Install the required packages
    import customtkinter as CTk
    from PIL import Image
    from apihandler import APIHandler
    from ydkhandler import YDKHandler
    from config import * # Import everything from config.py without having to name it every time

# Initialize constants
resolution_split: list[str] = WINDOW_RESOLUTION.split("x")
WINDOW_WIDTH, WINDOW_HEIGHT = int(resolution_split[0]),int(resolution_split[1])

# Initialize the APIHandler and YDKHandler classes
api_handler = APIHandler()
ydk_handler = YDKHandler()

class App(CTk.CTk):
    def __init__(self):
        # Initialize the main window
        CTk.set_appearance_mode("dark") # Force appearance mode to dark
        self.root = CTk.CTk() # Create the main window class
        self.root.geometry(WINDOW_RESOLUTION) # Set the window resolution
        self.root.resizable(False, False) # Disable window resizing
        self.root.grid_columnconfigure(0, weight=1) # Set the column to expand with the window
        self.root.grid_rowconfigure(0, weight=1) # Set the row to expand with the window

        # Set centered window title and icon
        self.root.title("Tracer") # TODO center the title string
        if os.name == "nt": # If the OS is Windows
            self.root.iconbitmap("./img/icon.ico")

        # Initial menu window

        # Load the program logo
        main_logo_label: CTk.CTkLabel = self.load_img("./img/placeholder_icon.png", img_position=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2-100), anchor="center")

        # Load new file button

    def show_window(self):
        self.root.mainloop() # Start the main loop

    def load_img(self, img_path: str, img_position: tuple[int, int], img_size: tuple[int, int] = None, label_text: str = '', anchor: str = 'topleft') -> CTk.CTkLabel:
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
    
if __name__ == "__main__":
    app = App()
    app.show_window() # Start the main window
