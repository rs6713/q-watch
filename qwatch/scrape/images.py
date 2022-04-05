#%%
import pathlib
import os
from google_images_download import google_images_download

#os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "images")
OUTPUT_DIR = os.path.join(pathlib.Path(__file__).parent.parent.parent.absolute(), "IMAGES")

def download(movie_title, limit=5):
  """ Download images associated with movie_title to OUTPUT_DIR."""

  # Clear existing dir
  if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
  else:
    movie_path = os.path.join(OUTPUT_DIR, movie_title)
    if os.path.exists(movie_path):
      for filename in os.listdir(movie_path):
        file_path = os.path.join(movie_path, filename)
        print(file_path)
        # try:
        #   if os.path.isfile(file_path):
        #     os.unlink(file_path)
        # except Exception as e:
        #   print('Failed to delete %s. Reason: %s' % (file_path, e))

  # Download Images
  config = dict(
    limit=limit,
    keywords=movie_title,
    #image_directory,
    output_directory=OUTPUT_DIR,
    print_urls=True,
    chromedriver= 'path/chromedriver'
    #format = gif,
  )

  response = google_images_download.googleimagesdownload()
  absolute_image_paths = response.download(config)

  return absolute_image_paths

# from PIL import Image
# for filename in absolute_image_paths[0][query]:
#   try:
#       with Image.open(filename) as im:
#         #im.show()
#         display(im)
#   except :
#       print(f"Invalid: {filename}")
#       #os.remove(img_dir + "/" + filename)
