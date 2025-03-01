try:
    import os
    import customtkinter as CTk
    from CTkMessagebox import CTkMessagebox
    import tkinter as tk
    from tkinter import filedialog
    from PIL import Image, ImageTk, ImageDraw

except ImportError:
    import os
    os.system("pip install -r requirements.txt")
    import customtkinter as CTk
    from CTkMessagebox import CTkMessagebox
    import tkinter as tk
    from tkinter import filedialog
    from PIL import Image, ImageTk, ImageDraw

from config import keybinds, VERSION, DEFAULT_COLORS, ASK_YDK_IMPORT_CONFIRMATION
from utils import create_img, create_button
from datetime import datetime

class CanvasHandler: #TODO add possibility to discard current canvas and return to main menu
    def __init__(self, 
                 log_handler,
                 api_handler,
                 ydk_parser, 
                 root_window = None, 
                 sheet_name: str = None, 
                 canvas_color: str = DEFAULT_COLORS["ARROW"], 
                 arrow_color: str = DEFAULT_COLORS["CANVAS"]):
        
        self.root_window = root_window
        if sheet_name is not None: self.sheet_name = sheet_name # Set the sheet name to the provided value
        self.sheet_name = f"YGO_combo_sheet_{datetime.now().strftime('%Y-%m-%d')}" # Set the sheet name to the current date if no name is provided TODO implement logic to update the name with a number if a sheet with the same name already exists

        # Create tabview widget and its tabs
        self.tabs = CTk.CTkTabview(self.root_window)
        self.canvas_tab = self.tabs.add("Canvas")
        self.cards_tab = self.tabs.add("Cards")
        self.card_view_tab = self.tabs.add("Card search")
        self.help_tab = self.tabs.add("Help")

        # Initialize variables
        self.scale: float = 1.0 # The scale of the canvas
        self.log_handler = log_handler 
        self.ydk_parser = ydk_parser
        self.api_handler = api_handler
        self.drag_data = {"item": None, "highlighter": None, "x": 0, "y": 0} # Data used for dragging items on the canvas

        # CANVAS TAB
        # | Init widgets
        self.canvas: CTk.CTkCanvas = CTk.CTkCanvas(master = self.canvas_tab, bg = canvas_color)

        # TODO aggiungi intestazione a canvas con bottoni file, edit, ecc.. che poi aprono un menu a tendina con le varie opzioni
        
        # | Set the default color of the arrows
        self.arrow_color: str = arrow_color

        # | Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_left_button_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_button_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_button_press)

        self.canvas.bind("<B1-Motion>", self.on_left_mouse_drag)
        self.canvas.bind("<B3-Motion>", self.on_right_mouse_drag)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # | Place the widgets

        # CARDS TAB
        # | Init widgets
        self.cards_list_frame = CTk.CTkScrollableFrame(self.cards_tab, corner_radius=25, fg_color="#333333")
        #self.cards_list_frame.grid_propagate(flag=False) # Disable the grid propagation
        self.cards_details_frame = CTk.CTkFrame(self.cards_tab, corner_radius=25, fg_color="#333333")
        self.cards_details_frame.pack_propagate(False) # Disable the pack propagation (the frame will not resize to fit its children)
        self.cards_empty_label = CTk.CTkLabel(self.cards_list_frame, text="No cards in the list.\nPress \"Import from YDK\" button or go to \"Cards search\" tab to add cards.", 
                                              font=("Helvetica", 16))
        
        self.cards_tab_import_button = create_button(master=self.cards_details_frame,
                                                     type="text",
                                                     command=self.cards_tab_import_ydk_button,
                                                     text="Import from YDK",
                                                     button_size=(30, 10),
                                                     should_be_placed=False)
        
        # | Place the widgets
        self.cards_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True) # Pack the frame to the left
        self.cards_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, expand=True) # Pack the frame to the right
        self.cards_tab_import_button.pack(side=tk.BOTTOM, expand=False, padx=10, pady=10) # Pack the button to the bottom
        # Widgets that should be place inside of the scrollable frame are placed after required data is loaded            
        
        # CARD VIEW TAB
        # | Frame and relative widgets
        self.card_view_tab_frame = CTk.CTkFrame(self.card_view_tab, corner_radius=25, fg_color="#333333")
        self.card_view_tab_preview_image =  create_img(master=self.card_view_tab_frame, img_path="data/img/card_back_2.png", #TODO check for copyright on the images 
                                                       scale=0.30, should_be_placed=False)
        self.card_view_tab_preview_image_text = CTk.CTkLabel(self.card_view_tab_frame, text="Lorem Ipsum", font=("Helvetica", 16))
        
        #   | Label and entry
        self.card_view_tab_label = CTk.CTkLabel(self.card_view_tab, text="Enter name of card:", font=("Helvetica", 16))
        self.card_view_tab_entry = CTk.CTkEntry(self.card_view_tab, font=("Helvetica", 16))

        #   | Option menus and relative labels
        level_options: list[str] = ["Any", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        race_options: list[str] = ["Any", "Aqua", "Beast", "Beast-Warrior", "Cyberse", "Dinosaur", "Divine-Beast", "Dragon",
                        "Fairy", "Fiend", "Fish", "Insect", "Illusion", "Machine", "Plant", "Psychic", "Pyro", "Reptile", "Rock", 
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

        #   | Search buttons
        self.card_view_search_online_button = create_button(master = self.card_view_tab,
                                                     type = "text",
                                                     command = lambda: self.search_cards(online=True),
                                                     text = "Search online",
                                                     fg_color = "#555555",
                                                     button_size = (100, 30),
                                                     corner_radius=25,
                                                     should_be_placed=False)
        self.card_view_search_online_button.configure(state = "disabled") # Disable the online search button by default

        self.card_view_search_offline_button = create_button(master = self.card_view_tab,
                                                             type = "text",
                                                             command = lambda: self.search_cards(online=False),
                                                             text = "Search offline",
                                                             fg_color = "#555555",
                                                             button_size = (100, 30),
                                                             corner_radius=25,
                                                             should_be_placed=False)
        self.card_view_search_offline_button.configure(state = "disabled") # Disable the offline search button by default        

        # | Bind events
        self.card_view_tab_level_options.configure(command = lambda _: self.update_online_search_button_state())
        self.card_view_tab_race_options.configure(command = lambda _: self.update_online_search_button_state())
        self.card_view_tab_attribute_options.configure(command = lambda _: self.update_online_search_button_state())
        self.card_view_tab_type_options.configure(command = lambda _: self.update_online_search_button_state())
        self.card_view_tab_entry.bind("<KeyRelease>", self.update_online_search_button_state)

        # | Pack the widgets
        #   | Card preview frame
        self.card_view_tab_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False) # Pack the frame to the right
        self.card_view_tab_preview_image.pack(side=tk.TOP, fill=tk.BOTH, padx=50, pady=50) # Pack the image to the top
        self.card_view_tab_preview_image_text.pack(side=tk.TOP, fill=tk.BOTH, padx=50, pady=50) # Pack the text to the top

        #   | Search filters
        self.card_view_tab_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10) # Pack the label to the top
        self.card_view_tab_entry.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10) # Pack the entry to the top

        self.card_view_search_online_button.pack(side=tk.LEFT, padx=10, pady=10)  # Pack the button to the left with padding
        self.card_view_search_offline_button.pack(side=tk.LEFT, padx=10, pady=10)  # Pack the button to the left with padding

        self.card_view_tab_level_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_level_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        self.card_view_tab_race_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_race_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        self.card_view_tab_attribute_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_attribute_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        self.card_view_tab_type_label.pack(side=tk.LEFT, padx=10, pady=5) # Pack the label to the top
        self.card_view_tab_type_options.pack(side=tk.LEFT, padx=10, pady=5) # Pack the option menu to the top

        # CARD and CARD VIEW TAB
        icon_size = 50
        self.attributes_icons = {
            "dark": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/dark.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "light": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/light.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "fire": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/fire.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "water": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/water.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "wind": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/wind.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "earth": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/earth.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "divine":CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/divine.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "spell": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/spell.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "trap": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/trap.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text="")
        }

        self.races_icons = {
            "aqua": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/aqua.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "beast": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/beast.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "beast-warrior": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/beast_warrior.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "cyberse": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/cyberse.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "dinosaur": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/dinosaur.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "divine-beast": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/divine_beast.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "dragon": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/dragon.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "fairy": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/fairy.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "fiend": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/fiend.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "fish": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/fish.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "insect": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/insect.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "illusion": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/illusion.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""),
            "machine": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/machine.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "plant": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/plant.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "psychic": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/psychic.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "pyro": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/pyro.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "reptile": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/reptile.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "rock": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/rock.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "sea serpent": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/sea_serpent.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "spellcaster": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/spellcaster.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "thunder": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/thunder.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "warrior": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/warrior.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "winged beast": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/winged_beast.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "wyrm": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/wyrm.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text=""), 
            "zombie": CTk.CTkLabel(master=self.cards_details_frame,
                                image=CTk.CTkImage(Image.open("data/img/icons/zombie.png"), size=(icon_size, icon_size)),
                                width=icon_size,
                                height=icon_size,
                                text="")
        }

        # HELP TAB
        help_tab_frame = CTk.CTkFrame(self.help_tab)
        help_tab_frame.pack(fill=tk.BOTH, expand=True)

        # | Init widgets
        navigation_help_label_string = (
            "Navigation:\n\n"
            "Left click and drag to move the canvas.\n"
            "Right click and drag to select item.\n"
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

        # | Place the widgets
        self.navigation_help_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.keybinds_help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.IO_help_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.about_help_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        help_tab_frame.grid_rowconfigure(0, weight=1, uniform="row")
        help_tab_frame.grid_rowconfigure(1, weight=1, uniform="row")
        help_tab_frame.grid_columnconfigure(0, weight=1, uniform="col")
        help_tab_frame.grid_columnconfigure(1, weight=1, uniform="col")

        self.navigation_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.keybinds_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.IO_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.about_help_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Event handling functions

    def on_left_button_press(self, event):
        """
        Marks the position of the canvas when the left mouse button is pressed.
        """
        
        # Check if the user has pressed on an item with the tag "image"
        item = self.canvas.find_withtag("current") # Get the item that the user has clicked on
        if "image" not in self.canvas.gettags(item): # Check if the item has the tag "image"
            return

        # Highlight the image
        x1, y1, x2, y2 = self.canvas.bbox(item[0])
        self.drag_data["highlighter"] = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=5, tags="highlighter")

        # Store the item and its initial position
        self.drag_data["item"] = item
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_left_mouse_drag(self, event):
        """
        Moves the highlighted image when the left mouse button is dragged.
        """
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.canvas.move(self.drag_data["highlighter"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_left_button_release(self, event):
        """
        Resets the drag data when the left mouse button is released.
        """
        self.drag_data["item"] = None
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def on_mouse_wheel(self, event):
        """
        Zooms in or out of the canvas when the mouse wheel is scrolled.
        """

        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= scale_factor
        self.canvas.scale("all", event.x, event.y, scale_factor, scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_scroll(int(-1 * event.delta / 120), "units")
        self.canvas.yview_scroll(int(-1 * event.delta / 120), "units")

    def on_right_button_press(self, event):
        """
        Displays a small menu when the right mouse button is pressed prompting the user to select an action.

        params:
            event: tk.Event - The event object containing information about the event.
        raises: 
            None
        return:
            None
        """

        # Create a menus
        menu = tk.Menu(self.canvas, tearoff=0)

        # Add commands to the menus
        menu.add_command(label="Add arrow", command = lambda: self.add_arrow(event.x, event.y, event.x + 50, event.y + 50))
        menu.add_command(label="Add text", command = lambda: self.canvas.create_text(event.x, event.y, text="Hello, world!", font=("Helvetica", 16)))

        # Show the menu at the mouse position
        menu.tk_popup(event.x_root, event.y_root)

    def add_image(self, image_path, scale, x, y):
        """
        Adds an image to the canvas.

        params:
            image_path: str - The path to the image file.
            scale: float - The scale of the image.
            x: int - The x-coordinate of the image.
            y: int - The y-coordinate of the image.

        return: None

        raises: None
        """

        image = Image.open(image_path)
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        self.card_images.append(image)  # Keep a reference to avoid garbage collection
        self.canvas.create_image(x, y, image=image, anchor=tk.CENTER, tags="image")

    def add_arrow(self, x1, y1, x2, y2):
        """
        Adds an arrow to the canvas.

        params:
            x1: int - The x-coordinate of the starting point.
            y1: int - The y-coordinate of the starting point.
            x2: int - The x-coordinate of the ending point.
            y2: int - The y-coordinate of the ending point.

        return: None

        raises: None
        """

        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=self.arrow_color)

    def on_right_mouse_drag(self, event):
        """
        Drags the canvas when the right mouse button is pressed.
        """
        print("Right mouse drag")
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def focus_on_card(self, card):
        """
        Focuses on a card in the cards tab.
        Called when a card is pressed in the cards_list frame.

        params:
            card: Card - The card to focus on.

        return: 
            None

        raises:
            None
        """

        # Clear the details frame of the cards tab
        for widget in self.cards_details_frame.winfo_children():
            if widget != self.cards_tab_import_button:
                widget.destroy()

        # Create the image of the card and pack it
        image_size: int = int(624 * 0.3)
        card_label_clone: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_details_frame, 
                                                      image=CTk.CTkImage(card.pillow_images["cropped_small"], size=(image_size, image_size)), 
                                                      width=image_size,
                                                      height=image_size,
                                                      text="")
        
        # Create the text of the card and pack it
        card_effect_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_details_frame,
                                                       text=card.effect,
                                                       font=("Helvetica", 16),
                                                       wraplength=340)  # Set the maximum width (the text will wrap around if it exceeds this width)
        
        card_label_clone.pack(side=tk.TOP, pady=(25, 0))
        card_effect_label.pack(side=tk.TOP, pady=(25, 0))
        
    # I/O related functions

    def export_canvas_to_png(self, file_path): # TODO check if it works properly
        """
        Exports the current canvas to a PNG file.

        params: 
            file_path: str - The path to the file where the canvas will be saved.
        return: 
            None
        raises: 
            None
        """

        # Update the canvas to make sure all elements are drawn
        self.canvas.update()

        # Get the canvas bounding box
        bbox = self.canvas.bbox("all")

        # Create a new PIL image with the size of the bounding box
        image = Image.new("RGB", (bbox[2] - bbox[0], bbox[3] - bbox[1]), self.canvas["bg"])

        # Draw the canvas onto the PIL image
        draw = ImageDraw.Draw(image)
        for item in self.canvas.find_all():
            coords = self.canvas.coords(item)
            if len(coords) == 4:  # Rectangle or line
                draw.rectangle(coords, outline=self.arrow_color)
            elif len(coords) == 2:  # Text or image
                draw.text(coords, self.canvas.itemcget(item, "text"), fill=self.arrow_color)

        # Save the PIL image to the specified file path
        image.save(file_path + ".png")
        
    async def show(self):
        """
        Shows the canvas, and destroys the root window when the window is closed.
        """
        
        await self.log_handler.log(type="INFO", message=f"Created new sheet with name: {self.sheet_name}.") # Necessary here even if not logically correct to properly, log the sheet name if the user doesn't provide one (see first lines of init method)                                                                                                                                                                       
        self.canvas.pack(fill=tk.BOTH, expand=True)                                                   
        self.tabs.pack(fill=tk.BOTH, expand=True)

    def cards_tab_import_ydk_button(self) -> list[Image.Image]:
        """
        Imports the images from a YDK file and returns them as Pillow Image objects.


        params: ydk_file_path: str - The path to the YDK file.
        return: list[Image.Image] - A list of Pillow Image objects.
        """

        if ASK_YDK_IMPORT_CONFIRMATION:
            msg = CTkMessagebox(master=self.root_window, 
                                title="Import ydk file?", 
                                message="Are you sure you want to import a ydk file?\n All current added cards will be lost.",
                                icon="question", 
                                options=["Yes and don't ask again", "Yes", "Cancel"],
                                justify="center")
            
            if os.name=="nt": msg.configure(corner_radius=25) # Set the corner radius of the messagebox to 25 if the OS is Windows (custom corner radius is not possible in Linux check docs)
            
            response = msg.get()
            if response == "No": return
            if response == "Yes and don't ask again": self.set_config_ask_ydk_import_confirmation(False)
            

        ydk_file_path = filedialog.askopenfilename(filetypes=[("YDK files", "*.ydk"), ("All files", "*.*")])

        card_ids, card_data, card_img_paths = self.ydk_parser.read_ydk(ydk_file_path)

        self.card_images = [[ ], [ ], [ ]] # Clear the images list
        [self.add_image_to_list(img_path) for img_path in card_img_paths] # Add the images to the list as pillow images

    def search_cards(self, online: bool = True) -> dict:
        """
        Searches for a cards based on the user's input and displays it on the card view tab.
        """

        name = self.card_view_tab_entry.get()
        level = self.card_view_tab_level_options.get()
        race = self.card_view_tab_race_options.get()
        attribute = self.card_view_tab_attribute_options.get()
        type = self.card_view_tab_type_options.get()

        search_targets: list[str] = ["name", "level", "race", "attribute", "type"]
        search_targets_deep_copy = search_targets.copy() # Deep copy the search targets list to avoid errors when removing elements from the original list while iterating over it

        # Remove the "Any" values from the search targets 
        # (e.g if name variable is equals to "Any" remove the "name" target from the search targets list)
        for target in search_targets_deep_copy:
            if locals()[target] == "Any" or locals()[target] == "": # Additional check for the entry because it returns an empty string if the user doesn't input anything
                search_targets.remove(target)

        del search_targets_deep_copy # Delete the deep copy of the search targets list to free up memory
        
        search_data = {target: locals()[target] for target in search_targets} # Create a dictionary with the search targets and their values

        if online:
            card_jsons = self.api_handler.request_card_data(search_data) # Search for the card based on the user's input
        else:
            raise NotImplementedError("Offline search is not implemented yet.")

    def on_close(self):
        """
        Called when the window is closed.
        """
        for tab in self.tabs.winfo_children():
            for child in tab.winfo_children():
                child.destroy()
        self.root_window.destroy()

    # Setters

    def set_root_window(self, root_window):
        """
        Sets the root window of the canvas.
        Should be called before once before calling the show method.
        Necessary because trying to set the root window in the constructor of app.py causes the program to crash (recursion limit).

        params: root_window: tk.Tk - The root window of the canvas.
        return: None
        """
        self.root_window = root_window
        self.root_window.protocol("WM_DELETE_WINDOW", self.on_close) # Bind the on_close method to the close button of the window
        self.root_window.title(self.sheet_name) # Set the title of the window to the sheet name
    
    def add_image_to_list(self, image_path):
        """
        Adds a Pillow Image object to the list of images to be displayed on the canvas.

        params: image_path: str - The path to the image file.
        return: None	
        """
        print(f"Adding image: {image_path}")

        if "cards_small" in image_path:
            self.card_images[1].append(Image.open(image_path))
        elif "cards_cropped" in image_path:
            self.card_images[2].append(Image.open(image_path))
        elif "cards" in image_path:
            self.card_images[0].append(Image.open(image_path))

    def update_online_search_button_state(self):
        """
        Updates the state of the online search button based on the user's input.
        """

        if (self.card_view_tab_level_options.get() == "Any" and 
            self.card_view_tab_race_options.get() == "Any" and
            self.card_view_tab_attribute_options.get() == "Any" and
            self.card_view_tab_type_options.get() == "Any" and
            self.card_view_tab_entry.get() == ""):
            self.card_view_search_button.configure(state="disabled")
        else:
            self.card_view_search_button.configure(state="normal")

    def update_offline_search_button_state(self):
        """
        Updates the state of the offline search button based on the presence of cache.
        """

        if os.listdir("data/card_data") and os.listdir("data/img/cached_images/cards") and os.listdir("data/img/cached_images/cards_small") and os.listdir("data/img/cached_images/cards_cropped"):
            self.card_view_search_offline_button.configure(state="normal")
        else:
            self.card_view_search_offline_button.configure(state="disabled")

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

    def set_config_ask_ydk_import_confirmation(self, value: bool):
        """
        Sets the value of ASK_YDK_IMPORT_CONFIRMATION in config.py.
        """
        
        # Read the current contents of config.py
        with open("config.py", "r") as file:
            lines = file.readlines()
        
        # Modify the value of ASK_YDK_IMPORT_CONFIRMATION
        for i, line in enumerate(lines):
            if line.startswith("ASK_YDK_IMPORT_CONFIRMATION"):
                lines[i] = f"ASK_YDK_IMPORT_CONFIRMATION = {value}\n"
                break
        
        # Write the updated contents back to config.py
        with open("config.py", "w") as file:
            file.writelines(lines)

    # Getters

    def get_canvas_theme(self) -> str:
        """
        Returns the theme of the canvas.

        return: str (dark, light) - The theme of the canvas based on the canvas color.
        """
        
        canvas_color: str = self.canvas["bg"][1:] # Remove the "#" from the color string
        r, g, b = int(canvas_color[0:2], 16), int(canvas_color[2:4], 16), int(canvas_color[4:6], 16) # Convert to rgb
        brightness = (r * 299 + g * 587 + b * 114) / 1000 # Calculate the brightness of the color
        if brightness > 128: return "light" # If the brightness is greater than 128 return "light"
        return "dark" # Otherwise return "dark"