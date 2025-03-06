try:
    import os
    import customtkinter as CTk
    from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
    import tkinter as tk
    from tkinter import filedialog
    from PIL import Image, ImageTk, ImageDraw

except ImportError:
    import os
    os.system("pip install -r requirements.txt")
    import customtkinter as CTk
    from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
    import tkinter as tk
    from tkinter import filedialog
    from PIL import Image, ImageTk, ImageDraw

import config
from datetime import datetime

class SheetHandler: #TODO add possibility to discard current canvas and return to main menu
    def __init__(self, 
                 log_handler,
                 api_handler,
                 ydk_parser, 
                 root_window, 
                 sheet_name: str = None, 
                 canvas_color: str = config.DEFAULT_COLORS["ARROW"], 
                 arrow_color: str = config.DEFAULT_COLORS["CANVAS"]):
        
        self.root_window = root_window
        if sheet_name is not None: self.sheet_name = sheet_name # Set the sheet name to the provided value
        self.sheet_name = f"YGO_combo_sheet_{datetime.now().strftime('%Y-%m-%d')}" # Set the sheet name to the current date if no name is provided TODO implement logic to update the name with a number if a sheet with the same name already exists

        # Init widgets
        self.menu_bar = None # This widget has to be created in the show method to avoid it showing up in the main menu

        # | Create tabview widget and its tabs
        self.tabs = CTk.CTkTabview(master=self.root_window,
                                   bg_color="#242424",
                                   segmented_button_selected_color="#242424",
                                   segmented_button_selected_hover_color="#2b2b2b",
                                   segmented_button_unselected_hover_color="#2b2b2b",
                                   )
        canvas_tab = self.tabs.add("Canvas")
        cards_tab = self.tabs.add("Cards")
        card_search_tab = self.tabs.add("Card search")

        # Initialize variables
        self.scale: float = 1.0 # The scale of the canvas
        self.log_handler = log_handler 
        self.ydk_parser = ydk_parser
        self.api_handler = api_handler
        self.app = None # Reference to the main class (cannot be set here and has to be passed after main class initialization to avoid circular imports)
        self.drag_data = {"item": None, "highlighter": None, "x": 0, "y": 0} # Data used for dragging items on the canvas

        # CANVAS TAB
        # | Init widgets
        self.canvas: CTk.CTkCanvas = CTk.CTkCanvas(master=canvas_tab, 
                                                   bg=canvas_color)

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
        self.canvas.pack(fill=tk.BOTH, expand=True) 

        # CARDS TAB
        # | Init widgets
        self.cards_list_frame = CTk.CTkScrollableFrame(cards_tab, 
                                                       corner_radius=25, 
                                                       fg_color="#333333")
        self.cards_list_frame.grid_propagate(flag=False) # Disable the grid propagation (the frame will not resize to fit its children)
        self.cards_details_frame = CTk.CTkFrame(cards_tab, 
                                                corner_radius=25, 
                                                fg_color="#333333")
        self.cards_details_frame.pack_propagate(False) # Disable the pack propagation (the frame will not resize to fit its children)
        self.cards_tab_stats_frame = CTk.CTkFrame(master=self.cards_details_frame,
                                                  fg_color="#333333",
                                                  corner_radius=25)
        self.cards_tab_attrib_race_subtype_frame = CTk.CTkFrame(master=self.cards_tab_stats_frame, 
                                                                fg_color="#2b2b2b",
                                                                corner_radius=25)
        self.cards_tab_atk_def_level_frame = CTk.CTkFrame(master=self.cards_tab_stats_frame, 
                                                          fg_color="#2b2b2b",
                                                          corner_radius=25)
        
        self.cards_empty_label = CTk.CTkLabel(self.cards_list_frame, 
                                              text="No cards in list.\nPress \"Import from YDK\" button under \"Actions\" menu button to add cards.", 
                                              font=("Helvetica", 16))
        
        self.cards_tab_extradeck_label = CTk.CTkLabel(self.cards_list_frame,
                                                      text="Extra deck", 
                                                      font=("Helvetica", 16))
        
        self.cards_tab_sidedeck_label = CTk.CTkLabel(self.cards_list_frame,
                                                     text="Side deck", 
                                                     font=("Helvetica", 16))
        
        #  | Card details frame widgets
        self.card_label_clone = None
        self.card_effect_label = None
        self.card_name_label = None
        self.card_effect_frame = None

        # | Init necessary variables
        self.cards_in_list_width = int(624 * 0.3) # make this dinamically calculated with config.CARD_PER_ROW_IN_LIST
        self.cards_in_list_height = int(624 * 0.3)

        # | Place the widgets
        self.cards_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True) # Pack the frame to the left
        self.cards_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, expand=True) # Pack the frame to the right
        # Widgets that should be placed inside of self.cards_list_frame are placed after required data is loaded 
                   
        # CARD and CARD SEARCH TAB
        self.card_icon_size = 50
        self.level_icon: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_atk_def_level_frame,
                                                     image=CTk.CTkImage(Image.open(os.path.join("data", "img", "level.png")), size=(self.card_icon_size, self.card_icon_size)),
                                                     width=self.card_icon_size,
                                                     height=self.card_icon_size,
                                                     text="")
        self.rank_icon: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_atk_def_level_frame,
                                                     image=CTk.CTkImage(Image.open(os.path.join("data", "img", "rank.png")), size=(self.card_icon_size, self.card_icon_size)),
                                                     width=self.card_icon_size,
                                                     height=self.card_icon_size,
                                                     text="")              

        self.attributes_icons = {
            "DARK": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "dark.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "LIGHT": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "light.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "FIRE": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "fire.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "WATER": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "water.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "WIND": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "wind.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "EARTH": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "earth.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "DIVINE":CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "divine.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "SPELL": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "spell.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "TRAP": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "attributes", "trap.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text="")
        }

        self.races_icons = {
            "Aqua": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "aqua.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Beast": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "beast.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Beast-Warrior": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "beast_warrior.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Creator-God": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "creator_god.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Cyberse": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "cyberse.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Dinosaur": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "dinosaur.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Divine-Beast": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "divine_beast.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Dragon": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "dragon.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Fairy": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "fairy.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Fiend": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "fiend.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Fish": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "fish.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Insect": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "insect.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Illusion": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "illusion.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Machine": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "machine.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Plant": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "plant.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Psychic": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "psychic.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Pyro": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "pyro.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Reptile": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "reptile.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Rock": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "rock.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Sea serpent": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "sea_serpent.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Spellcaster": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "spellcaster.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Thunder": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "thunder.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Warrior": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "warrior.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Winged Beast": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "winged_beast.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Wyrm": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "wyrm.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""), 
            "Zombie": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "zombie.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Continuous": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Continuous.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Counter": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Counter.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Equip": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Equip.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Field": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Field.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Ritual": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Ritual.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Quick-Play": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Quick-Play.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text=""),
            "Normal": CTk.CTkLabel(master=self.cards_tab_attrib_race_subtype_frame,
                                image=CTk.CTkImage(Image.open(os.path.join("data", "img", "races", "Normal.png")), size=(self.card_icon_size, self.card_icon_size)),
                                width=self.card_icon_size,
                                height=self.card_icon_size,
                                text="")
        }

        # CARD SEARCH TAB
        # | Init widgets
        # | Frame necessary to properly organize the widgets
        self.card_search_tab_options_frame = CTk.CTkFrame(card_search_tab, 
                                                          corner_radius=25, 
                                                          fg_color="#333333")

        #   | Label and entry
        self.card_search_tab_label = CTk.CTkLabel(self.card_search_tab_options_frame, text="Enter name of card:", font=("Helvetica", 16))
        self.card_search_tab_entry = CTk.CTkEntry(self.card_search_tab_options_frame, font=("Helvetica", 16))

        #   | Option menus and relative labels
        level_options: list[str] = ["Any", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        race_options: list[str] = ["Any", "Aqua", "Beast", "Beast-Warrior", "Cyberse", "Dinosaur", "Divine-Beast", "Dragon",
                        "Fairy", "Fiend", "Fish", "Insect", "Illusion", "Machine", "Plant", "Psychic", "Pyro", "Reptile", "Rock", 
                        "Sea Serpent", "Spellcaster", "Thunder", "Warrior", "Winged Beast", "Wyrm", "Zombie"]
        attribute_options: list[str] = ["Any", "Dark", "Divine", "Earth", "Fire", "Light", "Water", "Wind"]
        type_options: list[str] = ["Any", "Effect", "Fusion", "Link", "Normal", "Pendulum", "Ritual", "Synchro", "Trap", "Xyz"]
        
        self.card_search_tab_level_label = CTk.CTkLabel(self.card_search_tab_options_frame, text="Level:", font=("Helvetica", 16))
        self.card_search_tab_level_options = CTk.CTkOptionMenu(self.card_search_tab_options_frame, values=level_options, fg_color="#333333", button_hover_color="#555555")
        
        self.card_search_tab_race_label = CTk.CTkLabel(self.card_search_tab_options_frame, text="Race:", font=("Helvetica", 16))
        self.card_search_tab_race_options = CTk.CTkOptionMenu(self.card_search_tab_options_frame, values=race_options, fg_color="#333333", button_hover_color="#555555")
        
        self.card_search_tab_attribute_label = CTk.CTkLabel(self.card_search_tab_options_frame, text="Attribute:", font=("Helvetica", 16))
        self.card_search_tab_attribute_options = CTk.CTkOptionMenu(self.card_search_tab_options_frame, values=attribute_options, fg_color="#333333", button_hover_color="#555555")
        
        self.card_search_tab_type_label = CTk.CTkLabel(self.card_search_tab_options_frame, text="Type:", font=("Helvetica", 16))
        self.card_search_tab_type_options = CTk.CTkOptionMenu(self.card_search_tab_options_frame, values=type_options, fg_color="#333333", button_hover_color="#555555")

        #   | Search buttons 
        self.card_search_tab_search_button = CTk.CTkButton(master=self.card_search_tab_options_frame,
                                                           text="Search",
                                                           fg_color="transparent",
                                                           bg_color="transparent",
                                                           hover_color="#5b5b5b",
                                                           hover=True,
                                                           border_color='#5b5b5b',
                                                           border_width=2,  # Set the border width
                                                           corner_radius=25,
                                                           command=self.search_cards
                                                        )

        # | Pack the widgets
        self.card_search_tab_label.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10) # Pack the label to the top with padding
        self.card_search_tab_entry.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10) # Pack the entry to the top with padding

        #   | Pack the contents of self.card_search_tab_options_frame
        self.card_search_tab_search_button.pack(side=tk.LEFT, padx=20, pady=10)  # Pack the button to the left with padding

        self.card_search_tab_level_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_search_tab_level_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        self.card_search_tab_race_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_search_tab_race_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        self.card_search_tab_attribute_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_search_tab_attribute_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        self.card_search_tab_type_label.pack(side=tk.LEFT, padx=20, pady=10) # Pack the label to the left with padding
        self.card_search_tab_type_options.pack(side=tk.LEFT, padx=20, pady=10) # Pack the option menu to the left with padding

        #   | Pack self.card_search_tab_options_frame
        self.card_search_tab_options_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

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

        # | Initialize necessary flags
        is_card_monster: bool = card.type not in ["Trap Card", "Spell Card"]  # Check if the card is a monster card
        is_card_effect_long: bool = len(card.effect) > 475  # Check if the card effect is considered long TODO figure out right threshold (changing pack padding values will change it)
        is_card_link_monster: bool = card.type == "Link Monster"  # Check if the card is a link monster
        card_label_present: bool = False  # Flag to check if the card label clone is present
        card_effect_label_present: bool = False  # Flag to check if the card effect label is present
        card_name_label_present: bool = False  # Flag to check if the card name label is present

        # | Unpack all widgets to prepare for the new card
        for widget in self.cards_details_frame.winfo_children(): 
            # Unpack all widgets in the cards_details_frame except those that can be reused to optimize performance
            if widget != self.card_label_clone or \
               widget != self.card_effect_label or \
               widget != self.card_name_label:
                widget.pack_forget()

            # Check if the widgets that can be reused are present (the flags are necessary so that if they are not updated the widgets are created)
            if widget == self.card_label_clone: card_label_present = True
            elif widget == self.card_effect_label: card_effect_label_present = True
            elif widget == self.card_name_label: card_name_label_present = True

        [widget.pack_forget() for widget in self.cards_tab_attrib_race_subtype_frame.winfo_children()]  # Clear the attribute and race sub frame
        [widget.pack_forget() for widget in self.cards_tab_atk_def_level_frame.winfo_children()]  # Clear the atk, def and level/rank sub frame
        [widget.pack_forget() for widget in self.cards_tab_stats_frame.winfo_children()]  # Clear the stats frame (the one that contains self.cards_tab_attrib_race_subtype_frame and self.cards_tab_atk_def_level_frame)

        # | Create new widgets
        if card_label_present: # Check if the card label clone is already in the cards_details_frame just change the image
            self.card_label_clone.configure(image=card.images["list"].cget("image"))
        else: # Else create a new card label clone
            self.card_label_clone = CTk.CTkLabel(master=self.cards_details_frame, # Create the image of the card (the card image has to be cloned so it can appear both in the list and in self.cards_details_frame)
                                            image=card.images["list"].cget("image"), 
                                            width=self.cards_in_list_width,
                                            height=self.cards_in_list_height,
                                            text="")

        #  | Create appropriate attribute icons for the card
        if card.type == "Trap Card": attribute_icon: CTk.CTkLabel = self.attributes_icons["TRAP"] # If the card is a trap set the attribute icon to the trap icon
        elif card.type == "Spell Card": attribute_icon: CTk.CTkLabel = self.attributes_icons["SPELL"] # If the card is a spell set the attribute icon to the spell icon
        else: attribute_icon: CTk.CTkLabel = self.attributes_icons[card.attribute] # Get the attribute icon from the dictionary

        #  | Creating appropriate race icon for the card
        race_icon: CTk.CTkLabel = self.races_icons.get(card.race, self.races_icons["Normal"])  # Get the race icon from the dictionary, default to "Normal" if not found

        #  | Create the name of the card
        if card_name_label_present: # Check if the card name label is already in the cards_details_frame
            self.card_name_label.configure(text=card.name)
        else:
            self.card_name_label = CTk.CTkLabel(master=self.cards_details_frame,
                                                text=card.name,
                                                font=("Helvetica", 20),
                                                wraplength=450) # Set the maximum width (the text will wrap around if it exceeds this width)

        #  | Create the text (and the summoning requirements if the card is an extra deck monster) of the card
        if is_card_effect_long:
            if self.card_effect_frame in self.cards_details_frame.winfo_children(): # Check if the card effect frame is already in the cards_details_frame
                self.card_effect_label.configure(text=card.effect)
            else:
                self.card_effect_frame = CTk.CTkScrollableFrame(master=self.cards_details_frame, 
                                                                corner_radius=25, 
                                                                width=450,
                                                                fg_color="#333333")
                if self.card_effect_label in self.card_effect_frame.winfo_children(): # Check if the card effect label is already in the cards_details_frame
                    self.card_effect_label.configure(text=card.effect)
                else:
                    self.card_effect_label = CTk.CTkLabel(master=self.card_effect_frame,
                                                        text=card.effect,
                                                        font=("Helvetica", 16),
                                                        wraplength=450) # Set the maximum width (the text will wrap around if it exceeds this width)
                    self.card_effect_label.pack()
        else:
            if card_effect_label_present: # Check if the card effect label is already in the cards_details_frame
                self.card_effect_label.configure(text=card.effect)
            else:
                self.card_effect_label = CTk.CTkLabel(master=self.cards_details_frame,
                                                      text=card.effect,
                                                      font=("Helvetica", 16),
                                                      wraplength=450) # Set the maximum width (the text will wrap around if it exceeds this width)
        
        #  | Create the stats labels
        if is_card_monster: # Check if the card is a monster card
            card_atk_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_atk_def_level_frame,
                                                        text=f"ATK: {card.atk}",
                                                        font=("Helvetica", 16))
            if not is_card_link_monster: # Check if the card is a link monster
                card_level_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_atk_def_level_frame,
                                                            text=f"{card.level}",
                                                            font=("Helvetica", 16))
                card_def_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_atk_def_level_frame,
                                                                text=f"DEF: {card.def_}",
                                                                font=("Helvetica", 16))
            else:
                card_def_label: CTk.CTkLabel = CTk.CTkLabel(master=self.cards_tab_atk_def_level_frame,
                                                            text=f"Link - {card.linkval}",
                                                            font=("Helvetica", 16))
            
        # | Pack the widgets
        vert_padding = 15  # Vertical padding between widgets (not in between stats frame and attribute/race/subtype frame)
        #  | Pack the contents of self.cards_tab_attrib_race_subtype_frame
        attribute_icon.pack(side=tk.LEFT, padx=(10, 5), pady=vert_padding)
        race_icon.pack(side=tk.LEFT, padx=(5, 10), pady=vert_padding) 

        #  | If the card if a monster pack the contents of self.cards_tab_atk_def_level_frame
        if is_card_monster:
            card_atk_label.pack(side=tk.LEFT, padx=(10, 5), pady=vert_padding)
            if not is_card_link_monster: # Check if the card is a link monster
                card_def_label.pack(side=tk.LEFT, padx=(10, 5), pady=vert_padding)
                if card.type != "XYZ Monster": self.level_icon.pack(side=tk.LEFT, padx=(10, 5), pady=vert_padding) # Pack the level icon if the card is not an XYZ monster
                else: self.rank_icon.pack(side=tk.LEFT, padx=(10, 5), pady=vert_padding) # Else pack the rank icon
                card_level_label.pack(side=tk.LEFT, padx=(10, 10), pady=vert_padding) # Pack the level label
            else:
                card_def_label.pack(side=tk.LEFT, padx=(10, 10), pady=vert_padding)
        
        #  | Pack the contents of self.cards_tab_stats_frame
        self.cards_tab_attrib_race_subtype_frame.pack(side=tk.LEFT, padx=(10, 5), pady=(vert_padding, vert_padding))
        if is_card_monster: self.cards_tab_atk_def_level_frame.pack(side=tk.LEFT, padx=(5, 10), pady=(vert_padding, vert_padding))

        #  | Pack the contents of self.cards_details_frame
        self.card_label_clone.pack(side=tk.TOP, pady=(vert_padding, 0)) # Pack the card image
        self.cards_tab_stats_frame.pack(side=tk.TOP, pady=(vert_padding, 0)) # Pack the stats frame
        self.card_name_label.pack(side=tk.TOP, pady=(vert_padding, 0)) # Pack the card name
        if not is_card_effect_long: self.card_effect_label.pack(side=tk.TOP, pady=(vert_padding, 0)) # If the card effect is not long pack the label directly into self.cards_details_frame
        else: self.card_effect_frame.pack(side=tk.TOP, pady=(vert_padding, 0)) # Else pack the scrollable frame
        
    # I/O related functions
    def export_canvas_as_img(self, file_path): # TODO check if it works properly
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
        
    def show(self) -> None:
        """
        Shows the canvas, and destroys the root window when the window is closed.
        """
        
        self.root_window.protocol("WM_DELETE_WINDOW", self.on_close) # Bind the on_close method to the close button of the window
        self.root_window.title(self.sheet_name) # Set the title of the window to the sheet name

        self.menu_bar = CTkMenuBar(master=self.root_window,
                                   bg_color="#242424")
        
        file_button = self.menu_bar.add_cascade(text="File",
                                                hover_color="#2b2b2b")
        file_dropdown = CustomDropdownMenu(widget=file_button)
        file_dropdown.add_option(option="Open", command=lambda: print("Opening sheet"))
        file_dropdown.add_option(option="Save", command=lambda: print("Saving sheet"))
        file_dropdown.add_option(option="Export as PNG", command=lambda: self.export_canvas_as_img(file_path=filedialog.asksaveasfilename(title="Save canvas as image", filetypes=[("PNG files", "*.png")])))
        
        action_button = self.menu_bar.add_cascade(text="Action",
                                                  hover_color="#2b2b2b")
        action_dropdown = CustomDropdownMenu(widget=action_button)
        action_dropdown.add_option(option="Import YDK", command=self.import_ydk)

        about_button = self.menu_bar.add_cascade(text="About",
                                                 hover_color="#2b2b2b")

        self.tabs.pack(fill=tk.BOTH, expand=True)

    def import_ydk(self):  
        """
        Reads new ydk file and updates the cards list.
        
        params:
            None
        return: 
            None
        raises:
            None
        """

        # Unfornately since customtkinter does not automatically move the other widgets place with grid placement when one is inserted in the middle of the grid
        # the code has to manually remove all the widgets and then repack them in the correct order.
        # Moving all the other widgets when inserting one in the middle of the grid would technically be possible but the frame would need still need to be cleared
        # and the amount of calculations needed would lead to diminishing returns in terms of performance (and a mess to implement and eventually debug). 

        ydk_path = filedialog.askopenfilename(title="Select YDK file", filetypes=[("YDK files", "*.ydk")]) # Open the file dialog to select a ydk file     
        if ydk_path == "": return # If the user didn't select a file return

        # Get the existing card IDs by creating a deep copy of ydk_parser.card_ids_already_processed
        existing_card_ids: list[int] = self.ydk_parser.card_ids_already_processed.copy()
        self.ydk_parser.read_ydk(ydk_path) # Read the ydk file, cache the data and create and store the card objects into the card_objects list
        new_card_ids: set[int] = set(self.ydk_parser.card_ids_already_processed) - set(existing_card_ids) # Calculate the new card IDs
        
        for deck_type in self.app.card_objects: # For each deck type in the card_objects list
            for card in self.app.card_objects[deck_type]: # For each card in the deck
                if card.id in new_card_ids: # If the card is newly added
                    card.create_images()
                    card.update_list_image(width=self.cards_in_list_width,
                                           height=self.cards_in_list_height) # Create the list image for the card

        self.cards_empty_label.pack_forget() # Remove the empty label
        [widget.grid_forget() for widget in self.cards_list_frame.winfo_children()] # Clear the cards_list_frame of any possible card labels

        # Figure out if the images should be cropped or not
        if config.USE_CROPPED_IMAGES: image_type: str = "list"
        else: image_type: str = "small"      

        # Place main deck images
        for i, card in enumerate(self.app.card_objects["main"]): # For each card in the main deck
            card.images[image_type].grid(row=i // config.CARD_PER_ROW_IN_LIST, column=i % config.CARD_PER_ROW_IN_LIST, padx=5, pady=5) # Pack the cropped small images in a grid with config.CARD_PER_ROW_IN_LIST per row
            card.images[image_type].bind("<Button-1>", lambda _, card=card: self.focus_on_card(card=card)) # Bind the cropped small image to a function to bring the card into focus in the card_details_frame

        # Place extra deck images
        if len(self.app.card_objects["extra"]) > 0: # If there are cards in the extra deck
            image_last_row: int = (len(self.app.card_objects["main"]) + config.CARD_PER_ROW_IN_LIST - 1) // config.CARD_PER_ROW_IN_LIST # Calculate the last row of the main deck images
            self.cards_tab_extradeck_label.grid(row=image_last_row + 1, column=0, columnspan=config.CARD_PER_ROW_IN_LIST, pady=(10, 10)) # Place the label in a new row after all the images
            start_index: int = (image_last_row + 2) * config.CARD_PER_ROW_IN_LIST # Calculate the start index for the extra deck images
            for i, card in enumerate(self.app.card_objects["extra"], start=start_index): # For each card in the extra deck
                card.images[image_type].grid(row=i // config.CARD_PER_ROW_IN_LIST, column=i % config.CARD_PER_ROW_IN_LIST, padx=5, pady=5) # Pack the cropped small images in a grid with config.CARD_PER_ROW_IN_LIST per row
                card.images[image_type].bind("<Button-1>", lambda _, card=card: self.focus_on_card(card=card)) # Bind the cropped small image to a function to bring the card into focus in the card_details_frame

        # Place side deck images
        if len(self.app.card_objects["side"]) > 0: # If there are cards in the side deck
            image_last_row: int = ((len(self.app.card_objects["main"]) + len(self.app.card_objects["extra"])) + config.CARD_PER_ROW_IN_LIST - 1) // config.CARD_PER_ROW_IN_LIST # Calculate the last row of the main deck and extra deck images plus one for the extra deck label
            self.cards_tab_sidedeck_label.grid(row=image_last_row + 1, column=0, columnspan=config.CARD_PER_ROW_IN_LIST, pady=(10, 10)) # Place the label in a new row after all the images
            start_index: int = (image_last_row + 2) * config.CARD_PER_ROW_IN_LIST # Calculate the start index for the side deck images
            for i, card in enumerate(self.app.card_objects["side"], start=start_index): # For each card in the side deck
                card.images[image_type].grid(row=i // config.CARD_PER_ROW_IN_LIST, column=i % config.CARD_PER_ROW_IN_LIST, padx=5, pady=5)
                card.images[image_type].bind("<Button-1>", lambda _, card=card: self.focus_on_card(card=card)) # Bind the cropped small image to a function to bring the card into focus in the card_details_frame
    
    def search_cards(self) -> dict:
        """
        Searches for a cards based on the user's input and displays it on the card view tab.
        """

        name = self.card_search_tab_entry.get()
        level = self.card_search_tab_level_options.get()
        race = self.card_search_tab_race_options.get()
        attribute = self.card_search_tab_attribute_options.get()
        type = self.card_search_tab_type_options.get()

        search_targets: list[str] = ["name", "level", "race", "attribute", "type"]
        search_targets_deep_copy = search_targets.copy() # Deep copy the search targets list to avoid errors when removing elements from the original list while iterating over it

        # Remove the "Any" values from the search targets 
        # (e.g if name variable is equals to "Any" remove the "name" target from the search targets list)
        for target in search_targets_deep_copy:
            if locals()[target] == "Any" or locals()[target] == "": # Additional check for the entry because it returns an empty string if the user doesn't input anything
                search_targets.remove(target)

        del search_targets_deep_copy # Delete the deep copy of the search targets list to free up memory
        
        search_data = {target: locals()[target] for target in search_targets} # Create a dictionary with the search targets and their values

        raise NotImplementedError("Search function is not implemented yet.") # Raise an error to indicate that the function is not implemented yet

    def on_close(self) -> None: # TODO update to proper implementation
        """
        Called when the window is closed.
        """
        for tab in self.tabs.winfo_children():
            for child in tab.winfo_children():
                child.destroy()
        self.root_window.destroy()

    # Setters
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

    def update_list_images(self) -> None:
        """
        Creates the images of the cards for the list

        params:
            None
        raises:
            None
        returns:
            None
        """

        for deck_type in self.app.card_objects:
            for card in self.app.card_objects[deck_type]:
                card.update_list_image(width=self.cards_in_list_width, height=self.cards_in_list_height)

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