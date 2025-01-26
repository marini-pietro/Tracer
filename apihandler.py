try:
    import requests
except ImportError:
    import os
    os.system("pip install requests")
    del os
    import requests

BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php?"

class APIHandler:
    def __init__(self):
        pass

    def request_card_data(self, search_value, search_target) -> dict:
        """
        Request card data from the API.
        
        params:
            search_value: str The value to search for.
            search_target: str The target to search in. Can be 'name' or 'id'.
        returns:
            dict: The card data in JSON format.

        raises:
            ValueError: If the search target is not 'name' or 'id'.
        """

        if search_value not in ["name", "id"]:
            raise ValueError("Invalid search target. Please use 'name' or 'id'.")

        response = requests.get(BASE_URL + search_value + "=" + search_target)
        return response.json()