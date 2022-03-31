#%%
import pathlib
import os
from google_images_download import google_images_download
os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "images")
output_dir = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), "images")
print(output_dir)



# %%
query = "drool film"
config = dict(
  limit=5,
  keywords=query,
  #image_directory,
  output_directory=output_dir,
  print_urls=True,
  chromedriver= 'path/chromedriver'
  #format = gif,
)

response = google_images_download.googleimagesdownload()
absolute_image_paths = response.download(config)
# %%
from PIL import Image
for filename in absolute_image_paths[0][query]:
  try:
      with Image.open(filename) as im:
        #im.show()
        display(im)
  except :
      print(f"Invalid: {filename}")
      #os.remove(img_dir + "/" + filename)


# %%
