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

class App(CTk):
    def __init__(self): # TODO put code below inside of this class


# Initialize the main window
CTk.set_appearance_mode("dark") # Force appearance mode to dark
root = CTk.CTk() # Create the main window class
root.geometry(WINDOW_RESOLUTION) # Set the window resolution
root.resizable(False, False) # Disable window resizing
root.grid_columnconfigure(0, weight=1) # Set the column to expand with the window
root.grid_rowconfigure(0, weight=1) # Set the row to expand with the window

# Set centered window title and icon
root.title("Tracer") # TODO center the title string
if os.name == "nt": # If the OS is Windows
    root.iconbitmap("./img/icon.ico")

# Initial menu window

# Load the program logo
program_logo = Image.open("./img/placeholder_icon.png") # Open the image with pillow
program_logo_width, program_logo_height = program_logo.size # Get the size of the image
program_logo_image = CTk.CTkImage(program_logo, size=(256,256)) # Load the program logo into ctk image class
program_logo_label = CTk.CTkLabel(root, image=program_logo_image, text='') # Load the program logo into ctk label class
program_logo_label.pack() # Pack the program logo label
program_logo_label.place(x=WINDOW_WIDTH//2-program_logo_width//2, y=WINDOW_HEIGHT//2-program_logo_height//2-150) # Center the logo

# Load new file button


root.mainloop() # Start the main loop