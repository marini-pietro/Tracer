class YDKHandler:
    def __init__(self, api_handler):
        self.api_handler = api_handler

    def read_ydk(self, ydk_file):

        deck_position = {"main": 0, "extra": 1, "side": 2}
        card_data_output = [[], [], []] # main, extra, side

        with open(ydk_file, "r") as f:
            for line in f:
                line=line.strip() # remove leading and trailing whitespaces from the line (necessary for the following if statements) TODO look into this if this can be optimized
                if line == "#main":
                    position = deck_position["main"]
                    continue
                elif line == "#extra":
                    position = deck_position["extra"]
                    continue
                elif line == "!side":
                    position = deck_position["side"]
                    continue

                card_data = self.api_handler.request_card_data(search_value="id", search_target=line)
                card_data_output[position].append(card_data)


    def write_ydk(self, ydk_file, ydk): # TODO implement ydk writing
        raise NotImplementedError

    def cache_img(self, url):
        pass
