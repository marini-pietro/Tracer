import importlib, config
from os import listdir

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

    def is_dir_empty(directory):
        return len(listdir(directory)) == 0

    if is_dir_empty("data/img/cache/cards") and is_dir_empty("data/img/cache/cards_small") and is_dir_empty("data/img/cache/cards_cropped"): # If there are no cached images
        return False
    else: # If there are cached images
        return True