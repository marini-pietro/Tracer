try:
    import os, aiohttp, asyncio, time
except ImportError:
    import os
    os.system("pip install requests aiohttp")
    import aiohttp, asyncio, time

class YDKHandler:
    def __init__(self, api_handler):
        self.api_handler = api_handler
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

                card_ids_output[position].append(line) # add the card id to the list of card ids
                
                card_data: dict = self.api_handler.request_card_data(search_value="id", search_target=line) # request the card data from the API
                card_data_output[position].append(card_data) # add the card data to the list of card data

                cards_img_urls: list[str, str, str] = [card_data["data"][0]["card_images"][0]["image_url"], 
                                    card_data["data"][0]["card_images"][0]["image_url_small"],
                                    card_data["data"][0]["card_images"][0]["image_url_cropped"]] # get the card image URLs
                card_imgs_urls.append(cards_img_urls) # add the card image URLs to the list of card image URLs

                time.sleep(0.05) # sleep for 50 milliseconds to limit to 20 requests per second

            f.close()

        #Cache the images asynchronously
        asyncio.run(self.cache_images(card_imgs_urls))

        return card_ids_output, card_data_output


    def write_ydk(self, ydk_file, ydk): # TODO implement ydk writing
        raise NotImplementedError

    async def cache_images(self, card_imgs_urls):
        """
        Caches images from a list of card image URLs.

        params:
            card_imgs_urls: list[list[str, str, str]] A list of card image URLs. Each sublist contains the URLs for the full image, the small image and the cropped image.

        raises:
            None
        returns:
            None
        """

        tasks = [self.cache_img(url) for urls in card_imgs_urls for url in urls]
        await asyncio.gather(*tasks)

    async def cache_img(self, url):
        """
        Caches an image from a URL.

        params:
            url: str The URL of the image to cache.
        raises:
            None
        returns:
            None
        """

        BASE_CACHED_IMG_PATH: str = "img/cached_images/"
        print(f"Caching image from {url}", flush=True)
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
                else:
                    print(f"Failed to download image from {url}") # TODO implement logging

    def clear_cached_images(self):
        """
        Clears the cached images.

        params:
            None
        raises:
            None
        returns:
            None
        """

        BASE_CACHED_IMG_PATH: str = "img/cached_images/"
        for img_type in ["cards", "cards_small", "cards_cropped"]:
            img_path: str = os.path.join(BASE_CACHED_IMG_PATH, img_type)
            for img in os.listdir(img_path):
                final_path = os.path.join(img_path, img)
                if final_path.endswith(".jpg"): #Additional checks to avoid deleting .gitkeep files TODO remove this for deployment
                    os.remove(final_path)
