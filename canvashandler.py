try:
    import customtkinter as CTk
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    import os
    os.system("pip install customtkinter tkinter pillow")
    del os
    import customtkinter as CTk
    import tkinter as tk
    from tkinter import filedialog
    from PIL import Image, ImageTk, ImageDraw

from config import keybinds, VERSION
from utils import create_img, create_button
from datetime import datetime

class CanvasHandler: #TODO add possibility to discard current canvas and return to main menu
    def __init__(self, log_handler, root_window = None, sheet_name: str = None, canvas_color: str = "#ffffff", arrow_color: str = "#000000"):
        self.root_window = root_window
        self.log_handler = log_handler
        if sheet_name is not None: self.sheet_name = sheet_name # Set the sheet name to the provided value
        self.sheet_name = f"YGO_combo_sheet_{datetime.now().strftime('%Y%m%d')}" # Set the sheet name to the current date if no name is provided

        # Create tabview widget and its tabs
        self.tabs = CTk.CTkTabview(self.root_window)
        self.canvas_tab = self.tabs.add("Canvas")
        self.card_view_tab = self.tabs.add("Card View")
        self.help_tab = self.tabs.add("Help")

        # Initialize variables
        self.scale: float = 1.0
        self.images: list[Image.Image] = [[ ], [ ], [ ]] # full size, small size, cropped size

        #self.root_window.protocol("WM_DELETE_WINDOW", self.on_close) # Bind the on_close method to the close button of the window TODO implement this

        # CANVAS TAB
        # | Init widgets
        self.canvas: tk.Canvas = tk.Canvas(self.canvas_tab, bg=canvas_color)
        self.share_button: CTk.CTkButton = create_button(master=self.canvas_tab, type="image", command = lambda : self.export_canvas_to_png(filedialog.asksaveasfile()),  #TODO fix this (it looks very bad) and add file types and default extensions to asksaveasfile function
                                                         img_path="data/img/share_icon_light.png", button_size=(50, 50), 
                                                         should_be_placed=False)
        
        # | Set the default color of the arrows
        self.arrow_color: str = arrow_color

        # | Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_left_button_press)
        self.canvas.bind("<ButtonPress-3>", self.on_right_button_press)

        self.canvas.bind("<B1-Motion>", self.on_left_mouse_drag)
        self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # | Place the widgets
        self.share_button.place(relx=1.0, x=-60, y=10, anchor='ne')

        # HELP TAB
        help_tab_frame = CTk.CTkFrame(self.help_tab)
        help_tab_frame.pack(fill=tk.BOTH, expand=True)

        navigation_help_label_string = (
            "Navigation:\n\n"
            "Left click and drag to move the canvas.\n"
            "Right click and drag to select items.\n"
            "Scroll to zoom in and out."
        )
        keybinds_help_label_string = (
            "Keybinds:\n\n"
            f"{keybinds['arrow_placement']} - Place arrow\n"
            f"{keybinds['card_placement']} - Place card\n"
            f"{keybinds['delete_selected']} - Delete selected item(s)\n"
            f"{keybinds['move_selected']} - Move selected item(s)\n"
        )
        IO_help_label_string = (
            "Input/Output:\n\n"
            f"Ctrl + S - Save the current canvas\n"
            f"Ctrl + E - Export the current canvas as png image\n"
        )

        self.navigation_help_frame = CTk.CTkFrame(help_tab_frame, corner_radius=25)
        self.navigation_help_label = CTk.CTkLabel(
            self.navigation_help_frame, anchor="center", text=navigation_help_label_string, font=("Helvetica", 16)
        )
        self.keybinds_help_frame = CTk.CTkFrame(help_tab_frame, corner_radius=25)
        self.keybinds_help_label = CTk.CTkLabel(
            self.keybinds_help_frame, anchor="center", text=keybinds_help_label_string, font=("Helvetica", 16)
        )
        self.IO_help_frame = CTk.CTkFrame(help_tab_frame, corner_radius=25)
        self.IO_help_label = CTk.CTkLabel(
            self.IO_help_frame, anchor="center", text=IO_help_label_string, font=("Helvetica", 16)
        )
        self.about_help_frame = CTk.CTkFrame(help_tab_frame, corner_radius=25)
        self.about_help_label = CTk.CTkLabel(
            self.about_help_frame, anchor="center", text=f"About:\n\nOpen source created by Pietro Marini (marini-pietro on GitHub)\nVersion: {VERSION}", font=("Helvetica", 16)
        )

        # Pack the frames
        self.navigation_help_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.keybinds_help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.IO_help_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.about_help_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        help_tab_frame.grid_rowconfigure(0, weight=1, uniform="row")
        help_tab_frame.grid_rowconfigure(1, weight=1, uniform="row")
        help_tab_frame.grid_columnconfigure(0, weight=1, uniform="col")
        help_tab_frame.grid_columnconfigure(1, weight=1, uniform="col")

        # Pack the labels
        self.navigation_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.keybinds_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.IO_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.about_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # CARD VIEW TAB
        # | Frame and relative widgets
        self.card_view_tab_frame = CTk.CTkFrame(self.card_view_tab, corner_radius=25, fg_color="#333333")
        self.card_view_tab_preview_image =  create_img(master=self.card_view_tab_frame, img_path="data/img/card_back_2.png", #TODO check for copyright on the images 
                                                       scale=0.30, should_be_placed=False)
        self.card_view_tab_preview_image_text = CTk.CTkLabel(self.card_view_tab_frame, text="Lorem Ipsum", font=("Helvetica", 16))
        
        # | Label and entry
        self.card_view_tab_label = CTk.CTkLabel(self.card_view_tab, text="Enter name of card:", font=("Helvetica", 16))
        self.card_view_tab_entry = CTk.CTkEntry(self.card_view_tab, font=("Helvetica", 16))

        # | Option menus and relative labels
        level_options: list[str] = ["Any", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        race_options: list[str] = ["Any", "Aqua", "Beast", "Beast-Warrior", "Cyberse", "Dinosaur", "Divine-Beast", "Dragon",
                        "Fairy", "Fiend", "Fish", "Insect", "Machine", "Plant", "Psychic", "Pyro", "Reptile", "Rock", 
                        "Sea Serpent", "Spellcaster", "Thunder", "Warrior", "Winged Beast", "Wyrm", "Zombie"]
        attribute_options: list[str] = ["Any", "Dark", "Divine", "Earth", "Fire", "Light", "Water", "Wind"]
        type_options: list[str] = ["Any", "Effect", "Fusion", "Link", "Normal", "Pendulum", "Ritual", "Synchro", "Trap", "Xyz"]
        
        self.card_view_tab_level_label = CTk.CTkLabel(self.card_view_tab, text="Level:", font=("Helvetica", 16))
        self.card_view_tab_level_options = CTk.CTkOptionMenu(self.card_view_tab, values=level_options, fg_color="#333333", button_hover_color="#555555")
        
        self.card_view_tab_race_label = CTk.CTkLabel(self.card_view_tab, text="Race:", font=("Helvetica", 16))
        self.card_view_tab_race_options = CTk.CTkOptionMenu(self.card_view_tab, values=race_options, fg_color="#333333", button_hover_color="#555555")
        
        self.card_view_tab_attribute_label = CTk.CTkLabel(self.card_view_tab, text="Attribute:", font=("Helvetica", 16))
        self.card_view_tab_attribute_options = CTk.CTkOptionMenu(self.card_view_tab, values=attribute_options, fg_color="#333333", button_hover_color="#555555")
        
        self.card_view_tab_type_label = CTk.CTkLabel(self.card_view_tab, text="Type:", font=("Helvetica", 16))
        self.card_view_tab_type_options = CTk.CTkOptionMenu(self.card_view_tab, values=type_options, fg_color="#333333", button_hover_color="#555555")

        # | Pack the widgets
        #   | Card preview frame
        self.card_view_tab_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False) # Pack the frame to the right
        self.card_view_tab_preview_image.pack(side=tk.TOP, fill=tk.BOTH, padx=50, pady=50) # Pack the image to the top
        self.card_view_tab_preview_image_text.pack(side=tk.TOP, fill=tk.BOTH, padx=50, pady=50) # Pack the text to the top

        #   | Search filters
        self.card_view_tab_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10) # Pack the label to the top
        self.card_view_tab_entry.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10) # Pack the entry to the top

        self.card_view_tab_level_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_level_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        self.card_view_tab_race_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_race_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        self.card_view_tab_attribute_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_attribute_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        self.card_view_tab_type_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_type_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

    def add_image_to_list(self, image_path):
        """
        Adds a Pillow Image object to the list of images to be displayed on the canvas.

        params: image_path: str - The path to the image file.
        return: None	
        """
        if "cards" in image_path: self.images[0].append(Image.open(image_path))
        elif "cards_small" in image_path: self.images[1].append(Image.open(image_path))
        elif "cards_cropped" in image_path: self.images[2].append(Image.open(image_path))

    def set_root_window(self, root_window):
        """
        Sets the root window of the canvas.
        Should be called before once before calling the show method.
        Necessary because trying to set the root window in the constructor of app.py causes the program to crash (recursion limit).

        params: root_window: tk.Tk - The root window of the canvas.
        return: None
        """
        self.root_window = root_window

    def set_canvas_color(self, color: str):
        """
        Sets the color of the canvas.

        params: color: str - The color of the canvas.
        return: None
        """
        self.canvas.configure(bg=color)

    def set_arrow_color(self, color: str):
        """
        Sets the color of the arrows.

        params: color: str - The color of the arrows.
        return: None
        """
        self.arrow_color = color

    def on_left_button_press(self, event):
        """
        Marks the position of the canvas when the left mouse button is pressed.
        """
        print("Left button pressed")
        self.canvas.scan_mark(event.x, event.y)

    def on_left_mouse_drag(self, event):
        """
        Drags the canvas when the left mouse button is pressed.
        """
        print("Left mouse drag")
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_mouse_wheel(self, event):
        """
        Zooms in or out of the canvas when the mouse wheel is scrolled.
        """
        print("Mouse wheel scrolled")
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= scale_factor
        self.canvas.scale("all", event.x, event.y, scale_factor, scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_right_button_press(self, event):
        """
        Marks the position of the canvas when the right mouse button is pressed.
        """
        print("Right button pressed")
        self.canvas.scan_mark(event.x, event.y)

    def on_right_mouse_drag(self, event):
        """
        Drags the canvas when the right mouse button is pressed.
        """
        print("Right mouse drag")
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def add_image(self, image_path, x, y):
        """
        Adds an image to the canvas.

        params:
            image_path: str - The path to the image file.
            x: int - The x-coordinate of the image.
            y: int - The y-coordinate of the image.

        return: None

        raises: None
        """

        print(f"Adding image at x={x} y={y}")
        image = Image.open(image_path)
        image = ImageTk.PhotoImage(image)
        self.images.append(image)  # Keep a reference to avoid garbage collection
        self.canvas.create_image(x, y, image=image, anchor=tk.CENTER)

    def export_canvas_to_png(self, file_path):
        """
        Exports the current canvas to a PNG file.

        params: file_path: str - The path where the PNG file will be saved.
        return: None
        """
        # Get the canvas width and height
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Create a new PIL image with the same size as the canvas
        image = Image.new("RGB", (canvas_width, canvas_height), "white")
        draw = ImageDraw.Draw(image)

        # Draw the canvas content onto the PIL image
        self.canvas.update()
        self.canvas.postscript(file=file_path + ".ps", colormode='color')

        # Convert the postscript file to a PNG file
        ps_image = Image.open(file_path + ".ps")
        ps_image.save(file_path, "png")

        # Remove the temporary postscript file
        os.remove(file_path + ".ps")

    def show(self):
        """
        Shows the canvas, and destroys the root window when the window is closed.
        """
        
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.tabs.pack(fill=tk.BOTH, expand=True)