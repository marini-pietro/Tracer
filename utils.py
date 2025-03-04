import os, importlib, config
import customtkinter as CTk
from PIL import Image

def set_config_variable(variable_name: str, value: str | int | bool) -> None:
        """
        Set a variable in the config module.

        params:
            variable_name (str): The name of the variable to set.
            value (str | int | bool): The value to set the variable to.
        raises:
            None
        returns:
            None
        """
        # Read the current contents of config.py
        with open("config.py", "r") as file:
            lines = file.readlines()

        # Modify the value of the specified variable
        for i, line in enumerate(lines):
            if line.startswith(variable_name):
                lines[i] = f"{variable_name} = {value}\n"
                break

        # Write the updated contents back to config.py
        with open("config.py", "w") as file:
            file.writelines(lines)

        # Reload the config module to reflect the changes
        importlib.reload(config)

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

def create_img(master, 
               img_path: str, 
               img_position: tuple[int, int] = None, 
               img_size: tuple[int, int] = None, 
               label_text: str = '', 
               scale: float = None, 
               resample: int = Image.LANCZOS,
               bg_color: str = "transparent",
               fg_color: str = "transparent") -> CTk.CTkLabel:
    """
    Loads an places image into the window with the given path, position and size.

    Args:
        master (CTk.CTkWindow): The window to place the image in.
        img_path (str): The path to the image file.
        img_position (tuple[int, int]): The position to place the image (only used if should_be_placed is omitted or set to True).
        img_size (tuple[int, int], optional): The size of the image. If None, the image size is used. Not recommended to use with scale parameter.
        label_text (str, optional): The text to display with the image. Defaults to ''.
        scale (float, optional): The scale of the image. Defaults to 1.0.
        resample (int, optional): The resampling filter to use when resizing the image. Defaults to Image.LANCZOS. Available algorithms (NEAREST, BOX, BILINEAR, HAMMING, BICUBIC, LANCZOS)
        bg_color (str, optional): The background color of the label (hex). Defaults to "transparent".
        fg_color (str, optional): The foreground color of the label (hex). Defaults to "transparent".
        
    Returns:
        CTk.CTkLabel: The label object containing the image.
        
    Raises: 
        FileNotFoundError: If the image file is not found.
        ValueError: If the image position or image size tuples are invalid.
    """

    # Check if the arguments are valid and raise an error if they are not
    if not os.path.exists(img_path): raise FileNotFoundError(f"Image file not found at path: {img_path}") # Check if the image file exists
    if img_position is not None and len(img_position) != 2: raise ValueError("Image position must be a tuple with 2 integers.") # Check if the image position is valid
    if img_position is not None and (img_position[0] < 0 or img_position[1] < 0): raise ValueError(f"Image position must be greater than 0.\nx={img_position[0]} y={img_position[1]}") # Check if the image position is valid
    if img_size is not None and len(img_size) != 2: raise ValueError("Image size must be a tuple with 2 integers.") # Check if the image size tuple lenght is valid
    if img_size is not None and (img_size[0] <= 0 or img_size[1] <= 0): raise ValueError("Image size must be greater than 0.") # Check if the image size is valid
    if resample not in [Image.NEAREST, Image.BOX, Image.BILINEAR, Image.HAMMING, Image.BICUBIC, Image.LANCZOS]: raise ValueError("Invalid resampling filter.") # Check if the resampling filter is valid
    if scale <= 0: raise ValueError("Scale must be greater than 0.") # Check if the scale is valid
    if fg_color.startswith("#") and len(fg_color) != 7: raise ValueError("Invalid fg_color.") # Check if the fg_color is valid
    if bg_color.startswith("#") and len(bg_color) != 7: raise ValueError("Invalid bg_color.") # Check if the bg_color is valid

    pillow_img = Image.open(img_path) # Open the image file

    if img_size is not None: 
        img_size = pillow_img.size
    elif scale is not None: 
        img_size = (int(img_size[0] * scale), int(img_size[1] * scale))
        pillow_img = pillow_img.resize(img_size, resample=resample) # Resize the image
    
    ctk_label = CTk.CTkLabel(master=master, 
                             width=img_size[0],
                             height=img_size[1],
                             image=CTk.CTkImage(pillow_img, size=img_size),
                             text=label_text,
                             bg_color=bg_color,
                             fg_color=fg_color) # Load the image into ctk label class

    return ctk_label
    
def create_button(master, 
                  button_size: tuple[int, int], 
                  command: callable, 
                  text: str = "",
                  fg_color: str = "#2b2b2b", 
                  text_color: str = "white",
                  button_position: tuple[int, int] = None, 
                  corner_radius: int = 25, 
                  hover: bool = True, 
                  hover_color: tuple[int, int, int] | str = None, 
                  border_color: tuple[int, int, int] | str = None, 
                  border_width: int = 2,
                  should_be_placed: bool = True,
                  state: str = "normal",
                  bg_color: str = "transparent") -> CTk.CTkButton:
    
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
        border_width (int, optional): The width of the button border. Defaults to 2.
        state (str, optional): The state of the button. Defaults to "normal".
        bg_color (str, optional): The background color of the button. Defaults to "transparent".
        
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
           hover_color = (int(min(fg_color[0]*0.75, 255)), int(min(fg_color[1]*0.75, 255)), int(min(fg_color[2]*0.75, 255))) # Set the hover color to a darker version of the fg color
    elif fg_color == "transparent" and hover_color is None: # If the fg_color is transparent and there is no specified hover color
        hover_color = "#2b2b2b"
         
    button = CTk.CTkButton(master=master, 
                            text=text, 
                            command=command, 
                            fg_color=fg_color, 
                            text_color=text_color, 
                            width=button_size[0], 
                            height=button_size[1], 
                            hover=hover, 
                            corner_radius=corner_radius, 
                            hover_color=hover_color, 
                            border_color=border_color, 
                            border_width=border_width,  # Ensure border_width is set
                            state=state,
                            bg_color=bg_color
                          ) # Create the button object

    if should_be_placed: button.place(x=button_position[0], y=button_position[1]) # Set the button position and size
    
    return button