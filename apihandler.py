import requests

BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php?"

class APIHandler:
    def __init__(self):
        pass

    def request_card_data(self, search_value, search_target):

        if search_value not in ["name", "id"]:
            raise ValueError("Invalid search target. Please use 'name' or 'id'.")

        response = requests.get(BASE_URL + search_target + "=" + search_value)
        return response.json()