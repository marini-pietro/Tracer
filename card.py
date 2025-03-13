from os import system as cmd
from os import path as os_path
import config

try:
   from customtkinter import CTkLabel, CTkImage
   from PIL import Image
except ImportError:
    cmd('pip install -r requirements.txt')
    from PIL import Image
    from customtkinter import CTkLabel, CTkImage

del cmd

class Card():
    def __init__(self,
                 id: int,
                 name: str,
                 effect: str, 
                 level: int,
                 atk: str,
                 def_: str,
                 race: str,
                 attribute: str,
                 deck_type: str,
                 type: str,
                 linkval: str,
                 ygoprodeck_url: str,
                 img_root_window):

        # Set the attributes
        self.id = id
        self.ygoprodeck_url = ygoprodeck_url
        self.deck_type = deck_type
        self.type = type
        self.linkval=linkval # The link value of the card (only for link monsters) (if the card is not a link monster, it will be None)
        self.level = level # The level of the card (only for monsters) (if the card is not a monster, it will be None)
        self.name = name # The name of the card
        self.attribute = attribute # The attribute of the card (e.g. "Fire", "Water", "Earth", "Wind", "Light", "Dark", "Divine") (checking if the card is a monster has to be handled externally to avoid needing to pas all the json data which would uselessly increasing the memory usage)
        self.race = race # The sub-type of the card (e.g. "Warrior", "Spellcaster", "Equip", "Continuos", etc.)
        # TODO change the line below so the last dot character is not replaced
        self.effect = effect.replace(".", "\n") # The effect of the card (replace dots or carriage returns with new lines to form a paragraph from a single line) 
        # (the replace function for \r is there because in some old extra deck cards there is \r\n instead of just \n)
        
        if atk == -1: self.atk = "?" # If the card has unknown attack
        elif atk == None : self.atk = None # If the card is not a monster
        else: self.atk = atk
        
        if def_ == -1: self.def_ = "?" # If the card has unknown defense
        elif def_ == None : self.def_ = None  # If the card is not a monster
        else: self.def_ = def_ 

        # Handle images paths and objects
        self.img_root_window = img_root_window
        self.images_paths: dict[str, str] = {
            "normal": os_path.join("data", "img", "cache", "cards", f"{id}.jpg"),
            "small": os_path.join("data", "img", "cache", "cards_small", f"{id}.jpg"),
            "cropped": os_path.join("data", "img", "cache", "cards_cropped", f"{id}.jpg")
        }

        self.pillow_images: dict[str, Image.Image] = {}
        self.images: dict[str, CTkLabel] = {}

    def create_images(self):
        self.pillow_images: dict[str, Image.Image] = {
            "normal": Image.open(self.images_paths["normal"]),
            "small": Image.open(self.images_paths["small"]),
            "cropped": Image.open(self.images_paths["cropped"])
        }

        self.images: dict[str, CTkLabel] = {
            "normal": CTkLabel(master=self.img_root_window,
                               image=CTkImage(self.pillow_images["normal"]),
                               width=self.pillow_images["normal"].width,
                               height=self.pillow_images["normal"].height,
                               text=""),
            "small": CTkLabel(master=self.img_root_window,
                              image=CTkImage(self.pillow_images["small"]),
                              width=self.pillow_images["small"].width,
                              height=self.pillow_images["small"].height,
                              text=""),
            "cropped": CTkLabel(master=self.img_root_window,
                                image=CTkImage(self.pillow_images["cropped"]),
                                width=self.pillow_images["cropped"].width,
                                height=self.pillow_images["cropped"].height,
                                text=""),
            "list": None
        }
        
    def update_list_image(self, width, height):
        """
        Creates the images of the card.

        Returns:
            None
        Params:
            None
        Raises:
            None
        """

        type_of_image = "cropped" if config.USE_CROPPED_IMAGES else "small"

        self.images["list"] = CTkLabel(master=self.img_root_window,
                                        image=CTkImage(self.pillow_images[type_of_image] , size=(width, height)),
                                        width=width,
                                        height=height,
                                        text="")
        
    def get_data_json(self):
        """
        Returns the json data of the card.

        Returns:
            str: The json data of the card.

        Params:
            None

        Raises:
            IOError: If the json file is not found.
        """

        json_file_path = os_path.join("data", "card_data", "{id}.json").format(id=self.id)
        if not os_path.exists(json_file_path):
            raise IOError(f"File not found: {json_file_path}")
        with open(json_file_path, 'r') as file:
            data = file.read()
        return data