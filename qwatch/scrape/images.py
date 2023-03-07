""" Scrape images associated with movie from google image search."""

from typing import List
import os
import pathlib
import logging

import sys
from os.path import dirname
try:
    # new_dir = os.path.join(pathlib.Path(
    #     __file__).parent.parent.absolute(), "google-images-download")
    # print(new_dir)
    # sys.path.append(new_dir)
    from .bing_scraper import googleimagesdownload
except Exception as e:
    raise ImportError('Oh no', e)

#from google_images_download import google_images_download


logger = logging.getLogger(__name__)

#os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "images")
OUTPUT_DIR = os.path.join(pathlib.Path(
    __file__).parent.parent.parent.absolute(), "IMAGES")


def scrape_movie_images(movie_title: str, movie_year: int = None, limit: int = 5) -> List[str]:
    """ Download images associated with movie_title to OUTPUT_DIR."""
    search_term = f"{movie_title}{' ' + str(movie_year) if movie_year is not None else ''}"

    # Clear existing dir
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    else:
        movie_path = os.path.join(OUTPUT_DIR, search_term)
        if os.path.exists(movie_path):
            for filename in os.listdir(movie_path):
                file_path = os.path.join(movie_path, filename)
                logger.debug("Existing movie image: %s", file_path)
                # try:
                #   if os.path.isfile(file_path):
                #     os.unlink(file_path)
                # except Exception as e:
                #   print('Failed to delete %s. Reason: %s' % (file_path, e))

    # Download Images
    logger.info(
        "Downloading %d images for movie: %s, search term: %s, to %s", limit, movie_title, search_term, OUTPUT_DIR
    )

    config = dict(
        limit=limit,
        url='https://www.bing.com/images/search?q=%s' % search_term.replace(
            ' ', '%20'),
        # image_directory,
        output_directory=OUTPUT_DIR,
        chromedriver='E:/Projects/scraping/chromedriver.exe',  # 'path/chromedriver',
        download=True
        # print_urls=False,
        # silent_mode=True,
        # print_size=False,
        # print_paths=False,
        #format = gif,
    )

    # --search 'honeybees on flowers' - -limit 10 - -download - -chromedriver ./chromedriver

    # response = google_images_download.googleimagesdownload()
    # absolute_image_paths = response.download(config)

    response = googleimagesdownload()
    # wrapping response in a variable just for consistency
    absolute_image_paths, errors = response.download(config)
    logger.info('Downloaded Image Paths: %s', str(absolute_image_paths))

    return list(absolute_image_paths.values())[0]  # [0][search_term]

# from PIL import Image
# for filename in absolute_image_paths[0][query]:
#   try:
#       with Image.open(filename) as im:
#         #im.show()
#         display(im)
#   except :
#       print(f"Invalid: {filename}")
#       #os.remove(img_dir + "/" + filename)
