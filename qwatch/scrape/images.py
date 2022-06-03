""" Scrape images associated with movie from google image search."""
import logging
import pathlib
import os
from typing import List
from google_images_download import google_images_download

logger = logging.getLogger(__name__)

#os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "images")
OUTPUT_DIR = os.path.join(pathlib.Path(
    __file__).parent.parent.parent.absolute(), "IMAGES")


def scrape_movie_images(movie_title: str, movie_year: int = None, limit: int = 5) -> List[str]:
    """ Download images associated with movie_title to OUTPUT_DIR."""
    search_term = f"{movie_title}{' ' + str(movie_year) if movie_year is not None else ''} film"

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
    logger.debug(
        "Downloading %d images for movie: %s", limit, movie_title
    )

    config = dict(
        limit=limit,
        keywords=search_term,
        # image_directory,
        output_directory=OUTPUT_DIR,
        print_urls=True,
        chromedriver='path/chromedriver'
        #format = gif,
    )

    response = google_images_download.googleimagesdownload()
    absolute_image_paths = response.download(config)

    return absolute_image_paths[0][search_term]

# from PIL import Image
# for filename in absolute_image_paths[0][query]:
#   try:
#       with Image.open(filename) as im:
#         #im.show()
#         display(im)
#   except :
#       print(f"Invalid: {filename}")
#       #os.remove(img_dir + "/" + filename)
