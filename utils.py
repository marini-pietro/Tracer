import os
import customtkinter as CTk
from PIL import Image

def clear_cache_button_logic() -> bool:
    """
    Checks if the cache directory is empty and returns a boolean value.
    Should be called everytime the user returns to a menu with the clear cache button.
    """

    def is_dir_empty(directory): # TODO remove this function for deployment (there will be no .gitkeep files in the directory)
        return all(file == ".gitkeep" for file in os.listdir(directory))

    if is_dir_empty("data/img/cached_images/cards") and is_dir_empty("data/img/cached_images/cards_small") and is_dir_empty("data/img/cached_images/cards_cropped"): # If there are no cached images
        return False
    else: # If there are cached images
        return True

def create_img(master, img_path: str, img_position: tuple[int, int] = (0,0), img_size: tuple[int, int] = None, 
               label_text: str = '', anchor: str = 'topleft', scale: float = 1.0, should_be_placed: bool = True) -> CTk.CTkLabel:
    """
    Loads an places image into the window with the given path, position and size.

    Args:
        master (CTk.CTkWindow): The window to place the image in.
        img_path (str): The path to the image file.
        img_position (tuple[int, int]): The position to place the image (only used if should_be_placed is omitted or set to True).
        img_size (tuple[int, int], optional): The size of the image. If None, the image size is used. Not recommended to use with scale parameter.
        label_text (str, optional): The text to display with the image. Defaults to ''.
        anchor (str, optional): The anchor point of the image (only used if should_be_placed is omitted or set to True). Defaults to 'topleft'.
        scale (float, optional): The scale of the image. Defaults to 1.0.
        should_be_placed (bool, optional): If the image should be placed in the window with the given tuple imp_position and the given anchor (if set to False img_position and achor can be omitted). Defaults to True.
        
    Returns:
        CTk.CTkLabel: The label object containing the image.
        
    Raises: 
        FileNotFoundError: If the image file is not found.
        ValueError: If the image position or image size tuples are invalid.
    """

    # Check if the arguments are valid and raise an error if they are not
    if not os.path.exists(img_path): raise FileNotFoundError(f"Image file not found at path: {img_path}") # Check if the image file exists
    if len(img_position) != 2: raise ValueError("Image position must be a tuple with 2 integers.") # Check if the image position is valid
    if (img_position[0] < 0 or img_position[1] < 0): raise ValueError(f"Image position must be greater than 0.\nx={img_position[0]} y={img_position[1]}") # Check if the image position is valid
    if img_size is not None and len(img_size) != 2: raise ValueError("Image size must be a tuple with 2 integers.") # Check if the image size tuple lenght is valid
    if img_size is not None and (img_size[0] <= 0 or img_size[1] <= 0): raise ValueError("Image size must be greater than 0.") # Check if the image size is valid
    if anchor not in ["topleft", "center", "bottomright", "topright", "bottomleft"]: raise ValueError("Invalid anchor point.") # Check if the anchor point is valid

    pillow_img: Image = Image.open(img_path) # Open the image with pillow
    if img_size is None: img_size = (int(pillow_img.width * scale), int(pillow_img.height * scale)) # If no size is provided, use the scaled image size
    else: img_size = (int(img_size[0] * scale), int(img_size[1] * scale)) # Apply the scale to the provided size
    pillow_img = pillow_img.resize(img_size) # Resize the image
    ctk_img = CTk.CTkImage(pillow_img, size=img_size) # Load the image into ctk image class with correct arguments
    ctk_label = CTk.CTkLabel(master=master, image=ctk_img, text=label_text) # Load the image into ctk label class

    if should_be_placed: # If the image should be placed in the window
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
    
def create_button(master, 
                  button_size: tuple[int, int], 
                  command: callable, 
                  text: str = "",
                  fg_color: str = "#2b2b2b", 
                  text_color: str = "white", 
                  type: str = "text", 
                  img_path: str = None,
                  button_position: tuple[int, int] = None, 
                  corner_radius: int = 25, 
                  hover: bool = True, 
                  hover_color: tuple[int, int, int] | str = None, 
                  border_color: tuple[int, int, int] | str = None, 
                  should_be_placed: bool = True) -> CTk.CTkButton:
    """
    Creates a button in the window with the given text, position, size and command.

    params:
        master (CTk.CTkWindow): The window to place the button in.
        text (str): The text to display on the button (only used if type is set to text, defaults to None).
        type (str): The type of the button. Can be "text" or "image".
        img_path (str): The path to the image file (only used if type is "image").
        button_position (tuple[int, int]): The position to place the button (only used if should_be_placed is omitted or set to true).
        should_be_placed (bool, optional): If the button should be placed in the window with the given tuple button_position. Defaults to True.
        button_size (tuple[int, int]): The size of the button.
        command (callable): The function to call when the button is clicked.
        fg_color (str, optional): The color of the button. Defaults to "blue".
        text_color (str, optional): The color of the text. Defaults to "white".
        corner_radius (int, optional): The corner radius of the button.
        hover (bool, optional): If the button should change color when hovered. Defaults to True.
        hover_color (tuple[int, int, int] | str, optional): The color of the button when hovered. Defaults to None.
        border_color (tuple[int, int, int] | str, optional): The color of the button border. Defaults to None.
        
    Returns:
        CTk.CTkButton: The button object.
        
    Raises:
        ValueError: If the button position or button size tuples are invalid.
    """

    # Check if the arguments are valid
    if button_position is not None and len(button_position) != 2: raise ValueError("Button position must be a tuple with 2 integers.") # Check if the button position is valid
    if button_position is not None and (button_position[0] <= 0 or button_position[1] <= 0): raise ValueError("Button position must be greater than 0.")
    if len(button_size) != 2: raise ValueError("Button size must be a tuple with 2 integers.")
    if (button_size[0] <= 0 or button_size[1] <= 0): raise ValueError("Button size must be greater than 0.")

    if isinstance(fg_color, tuple): # If fg_color is a tuple
        if hover_color is None: # If there is no specified hover color
           hover_color = (min(fg_color[0]*0.75, 255), min(fg_color[1]*0.75, 255), min(fg_color[2]*0.75, 255)) # Set the hover color to a darker version of the fg color
    elif fg_color == "transparent":
        hover_color = "#2b2b2b"
        
    if type == "text": button = CTk.CTkButton(master=master, text=text, command=command, fg_color=fg_color, text_color=text_color, width=button_size[0], height=button_size[1], hover=hover, corner_radius=corner_radius, hover_color=hover_color, border_color=border_color) # Create the button object
    elif type == "image": 
        ctk_img = CTk.CTkImage(Image.open(img_path), size=button_size) # Load the image into ctk image class with correct arguments
        button = CTk.CTkButton(master=master, image=ctk_img, 
                               command=command, fg_color=fg_color, 
                               text_color=text_color, width=button_size[0],
                               height=button_size[1], hover=hover, 
                               corner_radius=corner_radius, hover_color=hover_color, 
                               border_color=border_color, text=text) # Create the button object

    if should_be_placed: button.place(x=button_position[0], y=button_position[1]) # Set the button position and size
    
    return button