try:
    import os, aiohttp, asyncio, time, json
    from tkinter import filedialog
except ImportError:
    import os
    os.system("pip install -r requirements.txt")
    import aiohttp, asyncio, time, json
    from tkinter import filedialog

from card import Card

class YDKParser:
    def __init__(self, api_handler, log_handler):
        self.api_handler = api_handler
        self.log_handler = log_handler
        self.app = None

        self.semaphore = asyncio.Semaphore(20) # create a semaphore to limit the number of concurrent requests to 20
        self.lock = asyncio.Lock() # create a lock to ensure thread safety when writing to the self.card_img_paths_list

        self.card_data_output: list[dict] = [] # This list will contain all the card data dictionaries
        self.card_imgs_urls: list[list[str, str, str]] = [] # This list will contain all the card image URLs that need to be cached (passed to the cache_img function in thread)

    def read_ydk(self, ydk_file):
        """
        Reads a ydk file and returns the card ids and card data.

        params:
            ydk_file: str The path to the ydk file.

        returns:
            tuple[list[list[int], list[int], list[int]], list[list[dict], list[dict], list[dict]], list[list[str, str, str]]]: 
            The card ids, card data, and card image paths. The first list contains the card ids, the second list contains the card data, 
            and the third list contains the card image paths. The first list contains the main deck, the second list contains the extra deck, 
            the third list contains the side deck.
        """        

        ids_already_processed = [] # list of card ids that have already been processed (useful to minimize the number of necessary operations while discarting possible duplicates)

        with open(ydk_file, "r") as file:
            for line in file:
                line = line[:-1] # remove the newline character at the end of the line
                if line == "#main":
                    position = "main"
                    continue
                elif line == "#extra":
                    position = "extra"
                    continue
                elif line == "!side":
                    position = "side"
                    continue
                elif line == "": continue # skip empty lines

                has_api_been_called: bool = False # Flag to keep track if the API has been called for the card data (if it is not in a loop there is no need to wait to respect the API limit)
                card_data: dict = {} # The card data dictionary

                if not os.path.exists(os.path.join("data", "card_data", f"{line}.json")): # If the card data is not cached, request it from the API
                    has_api_been_called = True
                    card_data: dict = self.api_handler.request_card_data(search_data={"id": line})
                else: # If the card data is cached, read it from the file
                    with open(os.path.join("data", "card_data", f"{line}.json"), "r") as json_file:
                        card_data = json.load(json_file)
                    json_file.close()

                self.card_data_output.append(card_data) # add the card data to the list of card data
                self.card_imgs_urls.append(
                                        [card_data["data"][0]["card_images"][0]["image_url"], 
                                        card_data["data"][0]["card_images"][0]["image_url_small"],
                                        card_data["data"][0]["card_images"][0]["image_url_cropped"]]) # add the card image URLs to the list of card image URL

                card_type: str = card_data["data"][0]["type"] # get the card type from the card data

                # Check if the card is not already in the list of card objects
                if not line in ids_already_processed:
                    ids_already_processed.append(line) # add the card id to the list of card ids that have already been processed
                    self.app.card_objects[position].append( # add the card object to the list of card objects
                        Card(card_id=line,
                             name=card_data["data"][0]["name"],
                             card_type=card_type,
                             level=card_data["data"][0]["level"] if card_type not in ["Spell Card", "Trap Card"] else None,
                             atk=card_data["data"][0]["atk"] if card_type not in ["Spell Card", "Trap Card"] else None,
                             def_=card_data["data"][0]["def"] if card_type not in ["Spell Card", "Trap Card"] else None,
                             race=card_data["data"][0]["race"],
                             attribute=card_data["data"][0]["attribute"] if card_type not in ["Spell Card", "Trap Card"] else None,
                             effect=card_data["data"][0]["desc"] if "desc" in card_data["data"][0] else None,
                             deck_type=position)
                    )

                if has_api_been_called: time.sleep(0.05) # sleep for 50 milliseconds to limit to 20 requests per second (API limit)
                # (with other operations in the loop this could not be necessary but keeping is necessary to avoid possible bans from the API)

        # Cache the images asynchronously
        asyncio.run(self.cache_data())

        # Log that the ydk file has been read
        asyncio.run(self.log_handler.log(type="INFO", message=f"Read ydk file {ydk_file}."))

        # Create the card images (not possible in the loop that reads the file because the images need to be cached first)
        for deck_type in self.app.card_objects:
            for card in self.app.card_objects[deck_type]:
                card.create_images(img_root_window=self.app.canvas_handler.cards_list_frame)

        # Delete the card data and card image URLs lists to free up memory
        self.card_data_output = []
        self.card_imgs_urls = []
        del ids_already_processed

    def write_ydk(self, ydk_file_name): # TODO implement ydk writing
        """
        Writes self.card_data a ydk file.

        params:
            ydk_file_name: str The name of the ydk file to write.

        returns:
            None

        raises:
            None
        """

        ydk_file_path: str = filedialog.asksaveasfilename(defaultextension=".ydk", filetypes=[("YDK files", "*.ydk")], initialfile=ydk_file_name) # open a file dialog to save the ydk file

        with open(ydk_file_path, "w") as f:
            for i, card_ids in enumerate(self.card_ids_output):
                if i == 0: f.write("#main\n")
                elif i == 1: f.write("#extra\n")
                elif i == 2: f.write("!side\n")

                for card_id in card_ids:
                    f.write(card_id + "\n")

        asyncio.run(self.log_handler.log(type="INFO", message=f"Wrote ydk file {ydk_file_name}."))

    async def cache_data(self):
        """
        Caches images and JSON data from a list of card image URLs and card data.

        params:
            self.card_imgs_urls: list[list[str, str, str]] A list of card image URLs. Each sublist contains the URLs for the full image, the small image, and the cropped image.
            self.card_img_paths_list: list[list[str, str, str]] A list of lists containing the image paths for the full, small, and cropped images.
            self.card_data_output: list[list[dict], list[dict], list[dict]] A list of card data dictionaries.

        raises:
            None
        returns:
            None
        """
        
        img_tasks = [self.cache_img(url) for urls in self.card_imgs_urls for url in urls] # create a list of tasks to cache the images
        json_tasks = [self.cache_json(card_data) for card_data in self.card_data_output] # create a list of tasks to cache the card data
        
        tasks = img_tasks + json_tasks
        task_batch_size = 20

        for i in range(0, len(tasks), task_batch_size): # run the tasks in batches of 20
            batch = tasks[i:i + task_batch_size]
            await asyncio.gather(*batch)  # run the tasks asynchronously in batches

    async def cache_img(self, url):
        """
        Caches an image from a URL.

        params:
            url: str The URL of the image to cache.
            self.card_img_paths_list: list[list[str, str, str]] A list of lists containing the image paths for the full, small, and cropped images.
        raises:
            None
        returns:
            None
        """

        async with self.semaphore: # limit the number of concurrent threads to 20

            BASE_CACHED_IMG_PATH: str = "data/img/cached_images/"
            url_splits: list[str] = url.split("/")

            card_id: str = url_splits[-1][:-4] # get everything except the last 4 characters (".jpg") to get the card id
            img_type: str = url_splits[-2] # get the image type (e.g. cards, cards_small, cards_cropped)

            final_img_path: str = os.path.join(BASE_CACHED_IMG_PATH, img_type, card_id + ".jpg") # create the final image path

            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        if not os.path.exists(final_img_path):
                            with open(final_img_path, 'wb') as f:
                                f.write(await response.read())
                        
                            await self.log_handler.log(type="INFO", message=f"Downloaded image from {url} to {final_img_path}")
                    else:
                        await self.log_handler.log(type="ERROR", message=f"Failed to download image from {url}")

    async def cache_json(self, card_data: dict):
        """
        Caches card data to a JSON file named after the card id.

        params:
            card_data: dict - The card data to cache.
            semaphore: asyncio.Semaphore - The semaphore to limit the number of concurrent logic streams.
        raises:
            None
        returns:
            None
        """

        async with self.semaphore: # limit the number of concurrent threads to 20
            card_id: str = card_data["data"][0]["id"] # get the card id
            card_data_path = os.path.join("data", "card_data", f"{card_id}.json") # create the final card data path

            if not os.path.exists(card_data_path): # if the card data is not cached
                with open(card_data_path, "w") as json_file: # write the card data to the file
                    json.dump(card_data, json_file, indent=4) # indent the JSON file for better readability
                await self.log_handler.log(type="INFO", message=f"Cached card data for card id {card_id}")

    async def clear_cache(self):
        """
        Clears the cache.

        params:
            None
        raises:
            None
        returns:
            None
        """

        # Delete images
        BASE_CACHED_IMG_PATH: str = "data/img/cached_images/"
        for img_type in ["cards", "cards_small", "cards_cropped", "cards_cropped_small"]:
            img_path: str = os.path.join(BASE_CACHED_IMG_PATH, img_type)
            for img in os.listdir(img_path):
                final_path = os.path.join(img_path, img)
                if final_path.endswith(".jpg"): # Additional checks to avoid deleting .gitkeep files
                    os.remove(final_path)

        # Delete JSON files
        BASE_CACHED_CARD_DATA_PATH: str = "data/card_data/"
        for card_data in os.listdir(BASE_CACHED_CARD_DATA_PATH):
            final_path = os.path.join(BASE_CACHED_CARD_DATA_PATH, card_data)
            if final_path.endswith(".json"): # Additional checks to avoid deleting .gitkeep files
                os.remove(final_path)

        await self.log_handler.log(type="INFO", message="Cleared all cache.")
    
    def set_app_reference(self, app):
        """
        Sets the reference to the app.

        params:
            app: App The reference to the app.
        raises:
            None
        returns:
            None
        """

        self.app = app