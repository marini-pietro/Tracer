try:
    import requests
except ImportError:
    import os
    os.system("pip install -r requirements.txt")("pip install requests")
    del os
    import requests

BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php?"

class APIHandler:
    def __init__(self, log_handler):
        self.log_handler = log_handler

    def request_card_data(self, search_data: dict[str, str]) -> dict:
        """
        Request card data from the API.
        
        params:
            search_data: dict[str, str] - The targets to search in and the values to search for.
        returns:
            dict: The card data in JSON format.

        raises:
            ValueError: If any of the search targets are invalid.
        """

        # Check if all search targets are valid
        are_search_targets_valid: bool = all([search_target in ["name", "id", "level", "race", "attribute", "type"] for search_target in search_data.keys()])
        
        if not are_search_targets_valid: raise ValueError("Invalid search target. Please use 'name', 'id', 'level', 'race', 'attribute' or 'type'.")

        final_url = BASE_URL # Initialize the final URL

        # Add the search values and search targets to the URL
        for search_target, search_value in search_data.items():
            final_url += f"{search_target}={search_value}&"
  
        response = requests.get(final_url) # Send the request to the API
    
        if response.status_code != 200:
            self.log_handler.log(type="ERROR", message=f"Could not connect to the API at {final_url} with error code {response.status_code}.")

        return response.json()
    
