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

import config
from utils import create_img, create_button
from card import Card
from datetime import datetime

class SheetHandler: #TODO add possibility to discard current canvas and return to main menu
    def __init__(self, 
                 log_handler,
                 api_handler,
                 ydk_parser, 
                 root_window = None, 
                 sheet_name: str = None, 
                 canvas_color: str = config.DEFAULT_COLORS["ARROW"], 
                 arrow_color: str = config.DEFAULT_COLORS["CANVAS"]):
        
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
        self.app = None # Reference to the main class (cannot be set here and has to be passed after main class initialization to avoid circular imports)
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
        self.cards_list_frame = CTk.CTkScrollableFrame(self.cards_tab, 
                                                       corner_radius=25, 
                                                       fg_color="#333333")
        #self.cards_list_frame.grid_propagate(flag=False) # Disable the grid propagation
        self.cards_details_frame = CTk.CTkFrame(self.cards_tab, 
                                                corner_radius=25, 
                                                fg_color="#333333")
        self.cards_details_frame.pack_propagate(False) # Disable the pack propagation (the frame will not resize to fit its children)
        self.cards_tab_attrib_race_subtype_frame: CTk.CTkFrame = CTk.CTkFrame(master=self.cards_details_frame, 
                                                               corner_radius=25) # Create the necessary frame to properly organize the widgets in the cards_details_frame
        self.cards_tab_stats_frame: CTk.CTkFrame = CTk.CTkFrame(master=self.cards_details_frame, 
                                                      corner_radius=25) # Create the necessary frame to properly organize the widgets in the cards_details_frame
        self.cards_empty_label = CTk.CTkLabel(self.cards_list_frame, 
                                              text="No cards in the list.\nPress \"Import from YDK\" button or go to \"Cards search\" tab to add cards.", 
                                              font=("Helvetica", 16))
        
        self.cards_tab_extradeck_label = CTk.CTkLabel(self.cards_list_frame,
                                                      text="Extra deck", 
                                                      font=("Helvetica", 16))
        
        self.cards_tab_sidedeck_label = CTk.CTkLabel(self.cards_list_frame,
                                                     text="Side deck", 
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
        self.card_view_tab_label.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10) # Pack the label to the top with padding
        self.card_view_tab_entry.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10) # Pack the entry to the top with padding

        self.card_view_search_online_button.pack(side=tk.LEFT, padx=20, pady=10)  # Pack the button to the left with padding
        self.card_view_search_offline_button.pack(side=tk.LEFT, padx=20, pady=10)  # Pack the button to the left with padding

        self.card_view_tab_level_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_view_tab_level_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        self.card_view_tab_race_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_view_tab_race_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        self.card_view_tab_attribute_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_view_tab_attribute_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        self.card_view_tab_type_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_view_tab_type_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        # CARD and CARD VIEW TAB
        self.card_icon_size = 50
        self.level_icon: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_stats_frame,
                                                     image=CTk.CTkImage(Image.open(os.path.join("data", "img", "level.png")), size=(self.card_icon_size, self.card_icon_size)),
                                                     width=self.card_icon_size,
                                                     height=self.card_icon_size,
                                                     text="")
        self.rank_icon: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_stats_frame,
                                                     image=CTk.CTkImage(Image.open(os.path.join("data", "img", "rank.png")), size=(self.card_icon_size, self.card_icon_size)),
                                                     width=self.card_icon_size,
                                                     height=self.card_icon_size,
                                                     text="")              

        self.attributes_icons = {
            "DARK": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "dark.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "LIGHT": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "light.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "FIRE": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "fire.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "WATER": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "water.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "WIND": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "wind.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "EARTH": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "earth.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "DIVINE":CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "divine.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "SPELL": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "spell.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "TRAP": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "trap.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text="")
        }

        self.races_icons = {
            "Aqua": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "aqua.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Beast": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "beast.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Beast-Warrior": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "beast_warrior.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Cyberse": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "cyberse.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Dinosaur": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "dinosaur.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Divine-Beast": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "divine_beast.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Dragon": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "dragon.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Fairy": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "fairy.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Fiend": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "fiend.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Fish": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "fish.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Insect": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "insect.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Illusion": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "illusion.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Machine": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "machine.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Plant": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "plant.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Psychic": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "psychic.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Pyro": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "pyro.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Reptile": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "reptile.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Rock": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "rock.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Sea serpent": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "sea_serpent.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Spellcaster": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "spellcaster.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Thunder": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "thunder.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Warrior": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "warrior.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Winged Beast": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "winged_beast.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Wyrm": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "wyrm.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Zombie": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "zombie.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Continuous": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Continuous.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Counter": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Counter.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Equip": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Equip.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Field": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Field.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Ritual": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Ritual.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Quick-Play": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Quick-Play.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Normal": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "Normal.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text="")
        }

        # HELP TAB
        # | Init widgets
        navigation_help_label_string = (
            "Navigation:\n\n"
            "Left click and drag to move the canvas.\n"
            "Right click and drag to select item.\n"
            "Scroll to zoom in and out."
        )
        keybinds_help_label_string = (
            "Keybinds:\n\n"
            f"{config.keybinds['arrow_placement']} - Place arrow\n"
            f"{config.keybinds['card_placement']} - Place card\n"
            f"{config.keybinds['delete_selected']} - Delete selected item(s)\n"
            f"{config.keybinds['move_selected']} - Move selected item(s)\n"
        )
        IO_help_label_string = (
            "Input/Output:\n\n"
            f"Ctrl + S - Save the current canvas\n"
            f"Ctrl + E - Export the current canvas as png image\n"
        )

        self.navigation_help_frame = CTk.CTkFrame(self.help_tab, corner_radius=25, fg_color="#333333")
        self.navigation_help_label = CTk.CTkLabel(
            self.navigation_help_frame, anchor="center", text=navigation_help_label_string, font=("Helvetica", 16)
        )
        self.keybinds_help_frame = CTk.CTkFrame(self.help_tab, corner_radius=25, fg_color="#333333")
        self.keybinds_help_label = CTk.CTkLabel(
            self.keybinds_help_frame, anchor="center", text=keybinds_help_label_string, font=("Helvetica", 16)
        )
        self.IO_help_frame = CTk.CTkFrame(self.help_tab, corner_radius=25, fg_color="#333333")
        self.IO_help_label = CTk.CTkLabel(
            self.IO_help_frame, anchor="center", text=IO_help_label_string, font=("Helvetica", 16)
        )
        self.about_help_frame = CTk.CTkFrame(self.help_tab, corner_radius=25, fg_color="#333333")
        self.about_help_label = CTk.CTkLabel(
            self.about_help_frame, anchor="center", text=f"About:\n\nOpen source created by Pietro Marini (marini-pietro on GitHub)\nVersion: {config.VERSION}", font=("Helvetica", 16)
        )

        # | Place the widgets
        self.navigation_help_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.keybinds_help_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.IO_help_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.about_help_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.help_tab.grid_rowconfigure(0, weight=1, uniform="row")
        self.help_tab.grid_rowconfigure(1, weight=1, uniform="row")
        self.help_tab.grid_columnconfigure(0, weight=1, uniform="col")
        self.help_tab.grid_columnconfigure(1, weight=1, uniform="col")

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

    def focus_on_card(self, card) -> None:
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

        # | Unpack all widgets to prepare for the new card
        for widget in self.cards_details_frame.winfo_children(): # Unpack all widgets in the cards_details_frame
            if widget != self.cards_tab_import_button:
                widget.pack_forget()

        [widget.pack_forget() for widget in self.cards_tab_attrib_race_subtype_frame.winfo_children()]  # Clear the attribute and race frame
        [widget.pack_forget() for widget in self.cards_tab_stats_frame.winfo_children()]  # Clear the stats frame

        # | Initialize necessary flags
        is_card_monster: bool = card.type not in ["Trap Card", "Spell Card"]  # Check if the card is a monster card
        is_card_effect_long: bool = len(card.effect) > 425  # Check if the card effect is considered long TODO figure out right threshold (changing pack padding values will change it)

        # | Create new widgets
        card_label_clone = CTk.CTkLabel(master=self.cards_details_frame, # Create the image of the card (the card image has to be cloned so it can appear both in the list and in self.cards_details_frame)
                                               image=CTk.CTkImage(card.pillow_images["cropped_small"], 
                                                                  size=(card.pillow_images["cropped_small"].width, 
                                                                        card.pillow_images["cropped_small"].height)), 
                                               width=card.pillow_images["cropped_small"].width,
                                               height=card.pillow_images["cropped_small"].height,
                                               text="")

        #  | Create appropriate attribute icons for the card
        if card.type == "Trap Card": attribute_icon: CTk.CTkLabel = self.attributes_icons["TRAP"] # If the card is a trap set the attribute icon to the trap icon
        elif card.type == "Spell Card": attribute_icon: CTk.CTkLabel = self.attributes_icons["SPELL"] # If the card is a spell set the attribute icon to the spell icon
        else: attribute_icon: CTk.CTkLabel = self.attributes_icons[card.attribute] # Get the attribute icon from the dictionary

        #  | Creating appropriate race icon for the card
        race_icon: CTk.CTkLabel = self.races_icons.get(card.race, self.races_icons["Normal"])  # Get the race icon from the dictionary, default to "Normal" if not found

        #  | Create the name of the card
        card_name_label = CTk.CTkLabel(master=self.cards_details_frame,
                                              text=card.name,
                                              font=("Helvetica", 20),
                                              wraplength=450) # Set the maximum width (the text will wrap around if it exceeds this width)

        #  | Create the text of the card
        if is_card_effect_long:
            card_effect_frame = CTk.CTkScrollableFrame(master=self.cards_details_frame, 
                                                              corner_radius=25, 
                                                              width=450,
                                                              fg_color="#333333")
            card_effect_label = CTk.CTkLabel(master=card_effect_frame,
                                                    text=card.effect,
                                                    font=("Helvetica", 16),
                                                    wraplength=450) # Set the maximum width (the text will wrap around if it exceeds this width)
            card_effect_label.pack()
        else:
            card_effect_label = CTk.CTkLabel(master=self.cards_details_frame,
                             text=card.effect,
                             font=("Helvetica", 16),
                             wraplength=450) # Set the maximum width (the text will wrap around if it exceeds this width)
        
        #  | Create the stats labels
        if is_card_monster: # Check if the card is a monster card
            card_atk_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_stats_frame,
                                                        text=f"ATK: {card.atk}",
                                                        font=("Helvetica", 16))
            card_def_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_stats_frame,
                                                        text=f"DEF: {card.def_}",
                                                        font=("Helvetica", 16))
            card_level_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_stats_frame,
                                                        text=f"{card.level}",
                                                        font=("Helvetica", 16))

        # | Pack the widgets
        #  | Pack the contents of self.cards_tab_attrib_race_subtype_frame
        attribute_icon.pack(side=tk.LEFT, padx=(10, 5), pady=20)
        race_icon.pack(side=tk.LEFT, padx=(5, 10), pady=20) 

        #  | If the card if a monster pack the contents of self.cards_tab_stats_frame
        if is_card_monster:
            card_atk_label.pack(side=tk.LEFT, padx=(10, 5), pady=20)
            card_def_label.pack(side=tk.LEFT, padx=(10, 5), pady=20)
            if card.type != "XYZ Monster": self.level_icon.pack(side=tk.LEFT, padx=(10, 5), pady=20) # Pack the level icon if the card is not an XYZ monster
            else: self.rank_icon.pack(side=tk.LEFT, padx=(10, 5), pady=20) # Else pack the rank icon
            card_level_label.pack(side=tk.LEFT, padx=(10, 10), pady=20) # Pack the level label
        
        #  | Pack the contents of self.cards_details_frame
        card_label_clone.pack(side=tk.TOP, pady=(20, 0)) # Pack the card image
        self.cards_tab_attrib_race_subtype_frame.pack(side=tk.TOP, pady=(20, 0)) # Pack the attribute
        if is_card_monster: self.cards_tab_stats_frame.pack(side=tk.TOP, pady=(20, 0)) # If the card is a monster pack the stats frame
        card_name_label.pack(side=tk.TOP, pady=(20, 0)) # Pack the card name
        if not is_card_effect_long: card_effect_label.pack(side=tk.TOP, pady=(20, 0)) # If the card effect is not long pack the label directly into self.cards_details_frame
        else: card_effect_frame.pack(side=tk.TOP, pady=(20, 0)) # Else pack the scrollable frame
        
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

    def cards_tab_import_ydk_button(self):  
        """
        Reads new ydk file and updates the cards list.	

        params:
            None
        return: 
            None
        raises:
            None
        """

        self.cards_empty_label.pack_forget() # Hide the empty label

        # Get the existing card IDs by creating a deep copy of ydk_parser.card_ids_already_processed
        existing_card_ids: list[int] = self.ydk_parser.card_ids_already_processed.copy()

        # Get necessary flags to avoid re-creating the labels
        was_extra_deck_present: bool = len(self.app.card_objects["extra"]) > 0 # Check if there are cards in the extra deck
        was_side_deck_present: bool = len(self.app.card_objects["side"]) > 0 # Check if there are cards in the side deck

        # Figure out if the images should be cropped or not
        if config.USE_CROPPED_IMAGES: 
            image_type: str = "cropped_small"
        else: 
            image_type: str = "small"

        # Loop through all the widgets in the cards_list_frame to figure out the last row and column values
        # Initialize the last row and column values to zero
        main_images_last_row: int = 0
        main_images_last_column: int = 0

        extra_images_last_row: int = 0
        extra_images_last_column: int = 0

        side_images_last_row: int = 0
        side_images_last_column: int = 0

        for widget in self.cards_list_frame.winfo_children():
            grid_info = widget.grid_info() # Get the grid information of the widget
            if self.app.card_objects["main"] and widget == self.app.card_objects["main"][-1].images[image_type]: # If the widget is the first main deck card image
                main_images_last_row = grid_info.get("row", 0) # Get the row of the last main deck card image
                main_images_last_column = grid_info.get("column", 0) # Get the column of the last main deck card image
            if self.app.card_objects["extra"] and widget == self.app.card_objects["extra"][-1].images[image_type]: # If the widget is the first extra deck card image
                extra_images_last_row = grid_info.get("row", 0) # Get the row of the last extra deck card image
                extra_images_last_column = grid_info.get("column", 0) # Get the column of the last extra deck card image
            if self.app.card_objects["side"] and widget == self.app.card_objects["side"][-1].images[image_type]: # If the widget is the first side deck card image
                side_images_last_row = grid_info.get("row", 0) # Get the row of the last side deck card image
                side_images_last_column = grid_info.get("column", 0) # Get the column of the last side deck card image

        # Read the ydk file and update the cards objects list (updates ydk_parser.card_ids_already_processed)
        ydk_file_path = filedialog.askopenfilename(filetypes=[("YDK files", "*.ydk"), ("All files", "*.*")])
        self.ydk_parser.read_ydk(ydk_file_path)

        # Get the new cards from the card objects list
        new_card_ids: set[int] = set(self.ydk_parser.card_ids_already_processed) - set(existing_card_ids) # Calculate the difference between ydk_parser.card_ids_already_processed and existing_card_ids
        new_cards: dict[str, list[Card]] = {
            "main": [card for card in self.app.card_objects["main"] if card.id in new_card_ids],
            "extra": [card for card in self.app.card_objects["extra"] if card.id in new_card_ids],
            "side": [card for card in self.app.card_objects["side"] if card.id in new_card_ids]
        }
        
        # Place main deck images
        if len(new_cards["main"]) > 0: # If there are new main deck cards to add
            start_row: int = main_images_last_row
            start_column: int = main_images_last_column + 1 if main_images_last_column != 0 else 0 
            start_index: int = start_row * config.CARD_PER_ROW_IN_LIST + start_column # Calculate the start index for the main deck images
            for i, card in enumerate(new_cards["main"], start=start_index): # For each card in the main deck
                card.images[image_type].grid(row=i // config.CARD_PER_ROW_IN_LIST, column=i % config.CARD_PER_ROW_IN_LIST, padx=5, pady=5) # Pack the cropped small images in a grid with config.CARD_PER_ROW_IN_LIST per row
                card.images[image_type].bind("<Button-1>", lambda _, card=card: self.focus_on_card(card=card)) # Bind the cropped small image to a function to bring the card into focus in the card_details_frame

            # Update the last row and column values because new main deck cards were added
            for widget in self.cards_list_frame.winfo_children():
                grid_info = widget.grid_info() # Get the grid information of the widget
                if self.app.card_objects["main"] and widget == self.app.card_objects["main"][-1].images[image_type]: # If the widget is the first main deck card image
                    main_images_last_row = grid_info.get("row", 0) # Get the row of the last main deck card image
                    main_images_last_column = grid_info.get("column", 0) # Get the column of the last main deck card image
                    break

        # Place extra deck images
        if len(new_cards["extra"]) > 0: # If there are new extra deck cards to add

            if len(new_cards["main"]) > 0: # If new main deck cards were added in the last for loop last row and column values should be updated
                for widget in self.cards_list_frame.winfo_children():
                    grid_info = widget.grid_info() # Get the grid information of the widget
                    if widget == self.app.card_objects["extra"][-1].images[image_type]: # If the widget is the first extra deck card image
                        extra_images_last_row = grid_info.get("row", 0) # Get the row of the last extra deck card image
                        extra_images_last_column = grid_info.get("column", 0) # Get the column of the last extra deck card image
                        break

            if not was_extra_deck_present: # If the extra deck was not present before the import
                self.cards_tab_extradeck_label.grid(row=extra_images_last_row + 1, column=0, columnspan=config.CARD_PER_ROW_IN_LIST, pady=(10, 10)) # Place the label in a new row after all the images
                start_row: int = extra_images_last_row + 2 # Set the start row to the row after the label
                start_column: int = 0 # If the extra deck was not present before the import the start column should be 0
            else:
                start_row: int = extra_images_last_row
                start_column: int = extra_images_last_column + 1 if extra_images_last_column != 0 else 0

            start_index: int = start_row * config.CARD_PER_ROW_IN_LIST + start_column # Calculate the start index for the extra deck images
            for i, card in enumerate(new_cards["extra"], start=start_index): # For each card in the extra deck
                card.images[image_type].grid(row=i // config.CARD_PER_ROW_IN_LIST, column=i % config.CARD_PER_ROW_IN_LIST, padx=5, pady=5) # Pack the cropped small images in a grid with config.CARD_PER_ROW_IN_LIST per row
                card.images[image_type].bind("<Button-1>", lambda _, card=card: self.focus_on_card(card=card)) # Bind the cropped small image to a function to bring the card into focus in the card_details_frame

            # Update the last row and column values because new extra deck cards were added
            for widget in self.cards_list_frame.winfo_children():
                grid_info = widget.grid_info() # Get the grid information of the widget
                if self.app.card_objects["extra"] and widget == self.app.card_objects["extra"][-1].images[image_type]: # If the widget is the first extra deck card image
                    extra_images_last_row = grid_info.get("row", 0) # Get the row of the last extra deck card image
                    extra_images_last_column = grid_info.get("column", 0) # Get the column of the last extra deck card image
                    break

        # Place side deck images
        if len(new_cards["side"]) > 0: # If there are new side deck cards to add

            # If new main deck or extra deck cards were added in the last for loop last row and column values should be updated
            if len(new_cards["main"]) > 0 or len(new_cards["extra"]) > 0: 
                for widget in self.cards_list_frame.winfo_children():
                    grid_info = widget.grid_info() # Get the grid information of the widget
                    if widget == self.app.card_objects["side"][-1].images[image_type]: # If the widget is the first side deck card image
                        side_images_last_row = grid_info.get("row", 0) # Get the row of the last side deck card image
                        side_images_last_column = grid_info.get("column", 0) # Get the column of the last side deck card image
                        break

            # If the side deck was not present before the import
            if not was_side_deck_present: 
                self.cards_tab_sidedeck_label.grid(row=side_images_last_row + 1, column=0, columnspan=config.CARD_PER_ROW_IN_LIST, pady=(10, 10)) # Place the label in a new row after all the images
                start_row: int = side_images_last_row + 2 # Set the start row to the row after the label
                start_column: int = 0 # If the side deck was not present before the import the start column should be 0 
            else:
                start_row: int = side_images_last_row
                start_column: int = side_images_last_column + 1 if side_images_last_column != 0 else 0

            start_index: int = start_row * config.CARD_PER_ROW_IN_LIST + start_column # Calculate the start index for the side deck images
            for i, card in enumerate(new_cards["side"], start=start_index): # For each card in the side deck
                card.images[image_type].grid(row=i // config.CARD_PER_ROW_IN_LIST, column=i % config.CARD_PER_ROW_IN_LIST, padx=5, pady=5)
                card.images[image_type].bind("<Button-1>", lambda _, card=card: self.focus_on_card(card=card)) # Bind the cropped small image to a function to bring the card into focus in the card_details_frame

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

    def on_close(self) -> None: # TODO update to proper implementation
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

    def set_app_reference(self, app):
        """
        Sets the reference to the app object.

        params: app: App - The app object.
        return: None
        """
        self.app = app

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