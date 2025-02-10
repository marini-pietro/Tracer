try:
    import os, aiohttp, asyncio, time, json
except ImportError:
    import os
    os.system("pip install requests aiohttp")
    import aiohttp, asyncio, time, json

class YDKParser:
    def __init__(self, api_handler, log_handler):
        self.api_handler = api_handler
        self.log_handler = log_handler
        self.deck_positions: dict[str, int] = {"main": 0, "extra": 1, "side": 2}

    def read_ydk(self, ydk_file):
        """
        Reads a ydk file and returns the card ids and card data.

        params:
            ydk_file: str The path to the ydk file.

        returns:
            tuple[list[list[int], list[int], list[int]], list[list[dict], list[dict], list[dict]]]: The card ids and card data. The first list contains the card ids, the second list contains the card data. The first list contains the main deck, the second list contains the extra deck, the third list contains the side deck.
        """        
        
        card_ids_output: list[list[int], list[int], list[int]] = [[], [], []] # main, extra, side
        card_data_output: list[list[dict], list[dict], list[dict]] = [[], [], []] # main, extra, side
        card_img_paths: list[list[str, str, str]] = [[], [], []] # This list will contain all the card image paths (full, small, cropped)
        card_imgs_urls: list[list[str, str, str]] = [] # This list will contain all the card image URLs that need to be cached (passed to the cache_img function in thread)

        with open(ydk_file, "r") as f:
            for line in f:
                line = line.strip() # remove leading and trailing whitespaces from the line (necessary for the following if statements) TODO look into this if this can be optimized
                if line == "#main":
                    position = self.deck_positions["main"]
                    continue
                elif line == "#extra":
                    position = self.deck_positions["extra"]
                    continue
                elif line == "!side":
                    position = self.deck_positions["side"]
                    continue
                elif line == "": continue # skip empty lines

                card_ids_output[position].append(line) # add the card id to the list of card ids
                
                if not os.path.exists(os.path.join("data", "card_data", f"{line}.json")): # If the card data is not cached, request it from the API
                    card_data: dict = self.api_handler.request_card_data(search_value="id", search_target=line)

                else: # If the card data is cached, read it from the file
                    with open(os.path.join("data", "card_data", f"{line}.json"), "r") as json_file:
                        card_data = json.load(json_file)
                    json_file.close()

                card_data_output[position].append(card_data) # add the card data to the list of card data

                cards_img_urls: list[str, str, str] = [card_data["data"][0]["card_images"][0]["image_url"], 
                                    card_data["data"][0]["card_images"][0]["image_url_small"],
                                    card_data["data"][0]["card_images"][0]["image_url_cropped"]] # get the card image URLs
                card_imgs_urls.append(cards_img_urls) # add the card image URLs to the list of card image URLs

                time.sleep(0.05) # sleep for 50 milliseconds to limit to 20 requests per second

            f.close()

        #Cache the images asynchronously
        asyncio.run(self.cache_data(card_imgs_urls, card_img_paths, card_data_output))

        self.log_handler.log(type="INFO", message=f"Read ydk file {ydk_file}.")

        return card_ids_output, card_data_output, card_img_paths


    def write_ydk(self, ydk_file, ydk): # TODO implement ydk writing
        raise NotImplementedError

    async def cache_data(self, card_imgs_urls, card_img_paths_list, card_data_output): # TODO update docstring
        """
        Caches images from a list of card image URLs.

        params:
            card_imgs_urls: list[list[str, str, str]] A list of card image URLs. Each sublist contains the URLs for the full image, the small image and the cropped image.

        raises:
            None
        returns:
            None
        """

        semaphore = asyncio.Semaphore(10) # create a semaphore to limit the number of concurrent requests to 20
        img_tasks = [self.cache_img(url, card_img_paths_list, semaphore) for urls in card_imgs_urls for url in urls] # create a list of tasks to cache the images
        json_tasks = [self.cache_json(card_data, semaphore) for deck_type in card_data_output for card_data in deck_type] # create a list of tasks to cache the card data
        
        tasks = img_tasks + json_tasks
        task_batch_size = 20

        for i in range(0, len(tasks), task_batch_size):
            batch = tasks[i:i + task_batch_size]
            await asyncio.gather(*batch)  # run the tasks asynchronously in batches

    async def cache_img(self, url, card_img_paths_list, semaphore): # TODO update docstring
        """
        Caches an image from a URL.

        params:
            url: str The URL of the image to cache.
        raises:
            None
        returns:
            None
        """

        async with semaphore: # limit the number of concurrent threads to 20

            BASE_CACHED_IMG_PATH: str = "data/img/cached_images/"
            url_splits: list[str] = url.split("/")

            card_id: str = url_splits[-1][:-4] # get everything except the last 4 characters
            img_type: str = url_splits[-2] # get the image type (e.g. cards, cards_small, cards_cropped)

            final_img_path: str = os.path.join(BASE_CACHED_IMG_PATH, img_type, card_id + ".jpg") # create the final image path

            # Download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        if not os.path.exists(final_img_path):
                            with open(final_img_path, 'wb') as f:
                                f.write(await response.read())
                                self.log_handler.log(type="INFO", message=f"Downloaded image from {url} to {final_img_path}")
                                # add the image path to the list of image paths based on the image type (used later in canvashandler to create pillow Image objects)
                                if img_type == "cards": card_img_paths_list[0].append(final_img_path)
                                elif img_type == "cards_small": card_img_paths_list[1].append(final_img_path)
                                elif img_type == "cards_cropped": card_img_paths_list[2].append(final_img_path)
                    
                    else: self.log_handler.log(type="ERROR", message=f"Failed to download image from {url}")

    async def cache_json(self, card_data, semaphore): # TODO update docstring
        """
        Caches card data to a json file named after the card id.
        """

        async with semaphore:
            # Cache the card data
            card_id: str = card_data["data"][0]["id"] # get the card id
            card_data_path = os.path.join("data", "card_data", f"{card_id}.json") # create the final card data path
            os.makedirs(os.path.dirname(card_data_path), exist_ok=True) # create the directories if they don't exist
            with open(card_data_path, "w") as json_file: # write the card data to the file
                json.dump(card_data, json_file, indent=4) # indent the json file for better readability
            json_file.close() # close the file

    def clear_cache(self):
        """
        Clears the cache.

        params:
            None
        raises:
            None
        returns:
            None
        """

        BASE_CACHED_IMG_PATH: str = "data/img/cached_images/"
        for img_type in ["cards", "cards_small", "cards_cropped"]:
            img_path: str = os.path.join(BASE_CACHED_IMG_PATH, img_type)
            for img in os.listdir(img_path):
                final_path = os.path.join(img_path, img)
                if final_path.endswith(".jpg"): #Additional checks to avoid deleting .gitkeep files TODO remove this for deployment
                    os.remove(final_path)

        BASE_CACHED_CARD_DATA_PATH: str = "data/card_data/"
        for card_data in os.listdir(BASE_CACHED_CARD_DATA_PATH):
            final_path = os.path.join(BASE_CACHED_CARD_DATA_PATH, card_data)
            if final_path.endswith(".json"): #Additional checks to avoid deleting .gitkeep files TODO remove this for deployment
                os.remove(final_path)

        self.log_handler.log(type="INFO", message="Cleared all cache.")
