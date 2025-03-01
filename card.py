from os import system as cmd
from os import path as os_path
from utils import create_img

try:
   from customtkinter import CTkLabel, CTkImage
   from PIL import Image
except ImportError:
    cmd('pip install -r requirements.txt')
    from PIL import Image
    from customtkinter import CTkLabel, CTkImage

class Card():
    def __init__(self,
                 card_id: str | int,
                 name: str,
                 effect: str, 
                 level: int,
                 atk: int | str,
                 def_: int | str,
                 race: str,
                 attribute: str,
                 deck_type: str,
                 card_type: str):

        # Check if arguments are valid and do the necessary conversions
        if not isinstance(card_id, str): 
            if not isinstance(card_id, int):
                card_id = str(card_id)
            else:
                raise TypeError(f"Expected str or int, got {type(card_id)}")
        if not isinstance(level, int) and level is not None:
            raise TypeError(f"Expected int, got {type(level)}")
        if not isinstance(atk, int) and atk is not None:
            raise TypeError(f"Expected int, got {type(atk)}")
        if not isinstance(def_, int) and def_ is not None:
            raise TypeError(f"Expected int, got {type(def_)}")
        if not isinstance(effect, str) and effect is not None:
            raise TypeError(f"Expected str, got {type(effect)}")

        # Set the attributes
        self.card_id = card_id
        self.deck_type = deck_type
        self.card_type = card_type
        self.name = name # The name of the card
        self.attribute = attribute # The attribute of the card (e.g. "Fire", "Water", "Earth", "Wind", "Light", "Dark", "Divine") (checking if the card is a monster has to be handled externally to avoid needing to pas all the json data which would uselessly increasing the memory usage)
        self.race = race # The sub-type of the card (e.g. "Warrior", "Spellcaster", "Equip", "Continuos", etc.)
        self.effect = effect.replace(". ", ".\n") # The effect of the card (replace the line breaks with new lines and the line)
        if card_type in ["Link Monster", "Xyz Monster", "Synchro Monster", "Fusion Monster"]: # If the card is an extra deck (so if it has a summoning requirement)
            self.effect.replace("\r\n", "\n\n") # Replace the line breaks with two new lines
        
        self.level = level if "Monster" in card_type else None # If the card is a monster card
        if atk == -1: self.atk = "?" # If the card has unknown attack
        elif atk == None : self.atk = None 
        else: self.atk = atk
        
        if def_ == -1: self.def_ = "?" # If the card has unknown defense
        elif def_ == None : self.def_ = None  # If the
        else: self.def_ = def_ 

        # Handle images paths and objects
        self.images_paths: dict[str, str] = {
            "normal": os_path.join("data", "img", "cached_images", "cards", f"{card_id}.jpg"),
            "small": os_path.join("data", "img", "cached_images", "cards_small", f"{card_id}.jpg"),
            "cropped": os_path.join("data", "img", "cached_images", "cards_cropped", f"{card_id}.jpg"),
            "cropped_small": os_path.join("data", "img", "cached_images", "cards_cropped_small", f"{card_id}.jpg")
        }

        self.pillow_images: dict[str, Image.Image] = {}

        self.images: dict[str, CTkLabel] = {}
        
        
    def create_images(self, img_root_window):
        """
        Creates the images of the card.

        Returns:
            None
        Params:
            img_root_window: The root window of the images.
        Raises:
            None
        """
        # TODO maybe add the option for images with rounded corners

        self.pillow_images: dict[str, Image.Image] = {
            "normal": Image.open(self.images_paths["normal"]),
            "small": Image.open(self.images_paths["small"]),
            "cropped": Image.open(self.images_paths["cropped"]),
            "cropped_small": Image.open(self.images_paths["cropped_small"] if os_path.exists(self.images_paths["cropped_small"]) 
                                                                           else self.images_paths["cropped"]).resize((int(624 * 0.3), int(624 * 0.3)), resample=Image.LANCZOS)
        }

        if not os_path.exists(self.images_paths["cropped_small"]): # If the image is not cached create it
            self.pillow_images["cropped_small"].save(os_path.join("data", "img", "cached_images", "cards_cropped_small", f"{self.card_id}.jpg")) # Cache the image

        self.images: dict[str, CTkLabel] = {
            "normal": CTkLabel(master=img_root_window,
                               image=CTkImage(self.pillow_images["normal"]),
                               width=self.pillow_images["normal"].width,
                               height=self.pillow_images["normal"].height,
                               text=""),
            "small": CTkLabel(master=img_root_window,
                              image=CTkImage(self.pillow_images["small"]),
                              width=self.pillow_images["small"].width,
                              height=self.pillow_images["small"].height,
                              text=""),
            "cropped": CTkLabel(master=img_root_window,
                                image=CTkImage(self.pillow_images["cropped"]),
                                width=self.pillow_images["cropped"].width,
                                height=self.pillow_images["cropped"].height,
                                text=""),
            "cropped_small": CTkLabel(master=img_root_window, 
                                     image=CTkImage(self.pillow_images["cropped_small"], size=(self.pillow_images["cropped_small"].width, self.pillow_images["cropped_small"].height)),
                                     width=self.pillow_images["cropped_small"].width,
                                     height=self.pillow_images["cropped_small"].height,
                                     text="")
        }

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

        json_file_path = os_path.join("data", "card_data", "{card_id}.json").format(card_id=self.card_id)
        if not os_path.exists(json_file_path):
            raise IOError(f"File not found: {json_file_path}")
        with open(json_file_path, 'r') as file:
            data = file.read()
        return data