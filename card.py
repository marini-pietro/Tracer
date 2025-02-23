from os import system as cmd
from os import path as os_path
from utils import create_img

try:
   from customtkinter import CTkLabel
except ImportError:
    cmd('pip install customtkinter')
    from customtkinter import CTkLabel

class Card():
    def __init__(self,
                 card_id: str | int,
                 effect: str, 
                 level: int,
                 atk: int,
                 def_: int,
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
        self.effect = effect
        self.level = level
        self.atk = atk
        self.def_ = def_
        self.race = race
        self.attribute = attribute
        self.card_id = card_id
        self.deck_type = deck_type
        self.card_type = card_type
        self.images_paths: dict[str, str] = {
            "normal": os_path.join("data", "img", "cached_images", "cards", "{card_id}.jpg").format(card_id=card_id),
            "small": os_path.join("data", "img", "cached_images", "cards_small", "{card_id}.jpg").format(card_id=card_id),
            "cropped": os_path.join("data", "img", "cached_images", "cards_cropped", "{card_id}.jpg").format(card_id=card_id)
        }

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

        self.images: dict[str, CTkLabel] = {
            "normal": create_img(master=img_root_window, 
                       img_path=self.images_paths["normal"],
                       should_be_placed=False),
            "small": create_img(master=img_root_window,
                      img_path=self.images_paths["small"],
                      should_be_placed=False),
            "cropped": create_img(master=img_root_window,
                        img_path=self.images_paths["cropped"],
                        should_be_placed=False)
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