#%%
from bs4 import BeautifulSoup
from IPython.display import display, HTML
import json
import pandas as pd
import re
import requests
import wikipedia
from googlesearch import search
import urllib


movies = [
  "Ammonite",
  "Drool",
  "The purple sea",
  "When night is falling",
  "Jenny's Wedding",
  "Gia",
  "But I'm a Cheerleader"
]
for idx in range(len(movies)):
  movie = movies[idx]

  suggestions = wikipedia.search(movie, results=5)
  print(suggestions)

  suggestions = wikipedia.search(movie + " (film)", results=5)
  print(suggestions)

movie = movies[4] 

#%%

summary = wikipedia.summary(movie + " (film)")
print(summary)
year = re.findall(r'[0-9]{4}', summary)[0]
#%%
url = wikipedia.page(movie).url
print(url)
# %%
html = wikipedia.page(movie).html()
page = BeautifulSoup(html, 'html.parser')

#print(page.prettify())
# %%
# p
# .infobox
properties = [
  "Directed by",
  "Written by",
  "Based on",
  "Starring",
  "Release date",
  "Running time",
  "Country",
  "Language"
]

def get_info(property):
  """ Get information from wikipedia infobox"""
  infobox = page.find("table", {"class": "infobox"})
  found = infobox.find("th", string=property)
  if found is not None:
    val = found.find_next_siblings("td")
    if len(val) > 0:
      return val[0].text
  return ""

page_info = {
  k: get_info(k) for k in properties
}
display(pd.Series(page_info))


# %%
def get_soup(url, header):
  print(url)
  return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url, None, header)),'html.parser')

query = "But Im a Cheerleader"
image_type = "ActiOn"
query = query.split()
query = '+'.join(query)
url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"

#add the directory for your image here
header = {
  'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
}
soup = get_soup(url, header)

images = [] # contains the link for Large original images, type of  image
for img in soup.find_all("img", {"class": "yWs4tf"}):
    #link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
    #ActualImages.append((link, Type))
    images.append(img["src"])
print(images)


# %%
import pathlib
import os
from google_images_download import google_images_download
os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "images")
output_dir = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), "images")
print(output_dir)



# %%
config = dict(
  limit=5,
  keywords="balloons",
  #image_directory,
  output_directory=output_dir,
  print_urls=True,

  #format = gif,
)

response = google_images_download.googleimagesdownload()
absolute_image_paths = response.download(config)

# %%
