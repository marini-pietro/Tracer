try:
    import requests
except ImportError:
    import os
    os.system("pip install -r requirements.txt")
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
            None
        """

        # Check if all search targets are valid
        are_search_targets_valid: bool = all([search_target in ["name", "fname", "id", "level", "race", "attribute", "type", "linkmarker"] for search_target in search_data.keys()])
        if not are_search_targets_valid:
            raise ValueError("Invalid search target. Please use 'name', 'id', 'level', 'race', 'attribute', 'type' or 'linkmarker'.")

        final_url: str = BASE_URL # Initialize the final URL

        # Add the search values and search targets to the URL
        final_url += '&'.join([f"{search_target}={search_value}" for search_target, search_value in search_data.items()]) + '&'

        try:
            response = requests.get(final_url[:-1]) # Send the request to the API (remove the last '&' from the URL)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx and 5xx)
        except requests.exceptions.RequestException as e:
            self.log_handler.log(type="ERROR", message=f"Could not connect to the API at {final_url} with error: {e}")
            return "Error"

        json_response = response.json()

        if 'error' in json_response:
            error_message = json_response['error']
            self.log_handler.log(type="ERROR", message=f"API error: {error_message}")
            return "Error"

        return json_response

