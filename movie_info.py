# %%
import urllib
from googlesearch import search
import wikipedia
import requests
import re
import pandas as pd
import json
from IPython.display import display, HTML
from bs4 import BeautifulSoup
import pathlib
import os
from IPython.display import display
from imdb import Cinemagoer
import uuid
from qwatch.io.input import get_id
from qwatch.io import _create_engine
from selenium import webdriver

# %%
from qwatch.scrape.imdb_api import IMDBScraper

scraper = IMDBScraper()
# %%
movie_title = 'blue is the warmest color'
cinema_goer = Cinemagoer()

movie_properties = {}
movies = cinema_goer.search_movie(movie_title)

movie_id = movies[0].movieID if len(movies) else None

# %%
movie_properties = cinema_goer.get_movie(
    movie_id,
    ['main', 'plot', 'synopsis', 'taglines']
)


# %%
movie_title = 'blue is the warmest color'

options = webdriver.ChromeOptions()
# options.add_argument('--headless')

# executable_path param is not needed if you updated PATH
browser = webdriver.Chrome(
    options=options,
    executable_path='E:/Projects/scraping/chromedriver.exe'
)
cinema_goer = Cinemagoer()

movie_properties = {}
movies = cinema_goer.search_movie(movie_title)

movie_id = movies[0].movieID if len(movies) else None


movie_properties = cinema_goer.get_movie(movie_id)

# Get IMDB Main page
movie_url = f"https://www.imdb.com/title/tt{movie_id}"
print(movie_url)
browser.get(movie_url)
movie_soup = BeautifulSoup(
    browser.page_source, "html.parser")
print(movie_soup)
# %%
tagline_section = movie_soup.find(
    "li", {"data-testid": "storyline-taglines"})

# %%
res = scraper.scrape("blue is the warmest color")

# %%
for k, v in res.items():
    print(k)
    print(v)
# %%

ia = Cinemagoer()

movies = ia.search_movie("rafiki 2018")
print(movies[0].movieID)
movie = ia.get_movie(movies[0].movieID)

# %%
print(movies[0].movieID)
url = f"https://www.imdb.com/title/tt{movies[0].movieID}"
#site = requests.get()
# browser = webdriver.PhantomJS()
# browser.get(url)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# executable_path param is not needed if you updated PATH
browser = webdriver.Chrome(
    options=options, executable_path='E:/Projects/scraping/chromedriver_new.exe')
browser.get(url)
html = browser.page_source

# html = browser.page_source#site.text
soup = BeautifulSoup(html, "html.parser")
# %%
soup.select('div:-soup-contains("Watch on BFI Player")')


# %%
box_office_box = soup.find("div", {"data-testid": "title-boxoffice-section"}).find_all(
    "li"
) if soup.find("div", {"data-testid": "title-boxoffice-section"}) is not None else []
box_offices = [
    b.find("div").text
    for b in box_office_box
    if b.find("span").text in ["Gross worldwide", "Cumulative Worldwide Gross"]
]
print("box office", box_offices)

budget = [
    b.find("div").text
    for b in box_office_box
    if b.find("span").text in ["Budget"]
]
print("budget", budget)

# %%
prime = [
    d.find_next_sibling("div").text
    for d in soup.select('div:-soup-contains("Watch on Prime Video")') if hasattr(d, "find_next_sibling") and d.find_next_sibling("div") is not None
]
prime_costs = [
    {"COST": float(re.findall(r'(?<=GBP)[0-9\.]+', p)[0])} if "rent/buy" in p
    else {"MEMBERSHIP_INCLUDED": True, "COST": None}
    for p in prime
    if "rent/buy" in p or p == "included with Prime"
]
prime_costs

# %%
# price = soup.find("div", text="Prime Video")
# prime = soup.select('div:-soup-contains("Prime Video")')
# price = None if not len(prime) else prime.find_next_sibling("div").text
# print(price)

taglines = soup.find("li", {"data-testid": "storyline-taglines"}).find(
    "div").text if soup.find("li", {"data-testid": "storyline-taglines"}) is not None else None
print("Taglines: ", taglines)

prime = [
    d.find_next_sibling("div").text
    for d in soup.select('div:-soup-contains("Watch on Prime Video")') if hasattr(d, "find_next_sibling") and d.find_next_sibling("div") is not None
]
prime_prices = [
    p for p in prime
    if "rent/buy" in p
]
print(prime_prices)

netflix = "Netflix" in soup.find(
    "li", {"data-testid": "title-details-companies"}).text
print("Netflix? ", netflix)

#TODO: Trailer
# TODO: Click on more watch options


# %%
MAX_QUOTES = 10
site = requests.get(f"https://www.imdb.com/title/tt{movies[0].movieID}/quotes")
soup = BeautifulSoup(site.text, "html.parser")
quotes = soup.find("div", id="quotes_content").find_all(
    "div", {"class": "quote"})
quotes = [
    list(zip(
        [par.text.split(":", 1)[0][1:] for par in quote.find_all(
            "p") if len(par.text.split(":")) > 1],
        [par.text.split(":", 1)[1][1:] for par in quote.find_all(
            "p") if len(par.text.split(":")) > 1]
    ))
    for quote in quotes[:MAX_QUOTES]
]
print(quotes)


# %%
genre_mappings = {
    "History": "Period-Piece",
    "Horror": "Horror/Thriller",
    "Thriller": "Horror/Thriller",
    "Sci-Fi": "Sci-Fi/Fantasy",
    "Action": "Action/Adventure",
    "Adventure": "Action/Adventure"
}

info = {
    "IMDB_ID": movie["imdbID"],
    "SUMMARY": movie.get("plot outline", None),
    "CERTIFICATE": ",".join(movie["certificates"]),
    "LANGUAGE": ", ".join([lc.upper() for lc in movie["language codes"]]),
    "GENRES": list(map(
        lambda g: genre_mappings.get(g, g),
        movie.get("genres", [])
    )),
    "BUDGET": movie.get("box office", {}).get("Budget", None),
    "BOX_OFFICE": movie.get("box office", {}).get("Cumulative Worldwide Gross", None),
    "RUNNING_TIME": movie.get("runtimes", [None])[0],
    "YEAR": movie.get("year", None),
    "TITLE": movie["title"],
    "ORIGINAL_TITLE": movie.get("original title", None),
    "COUNTRY": movie.get("countries", [None])[0],
}

imgdbID = movie.get("imdbID", None)
print(imgdbID)

display(info)

cast = movie["cast"]
MAX_CAST = 5
MAX_WRITER = 3
MAX_DIRECTOR = 3
ids = [
    uuid.uuid4().int & (1 << 64)-1
    for _ in np.arange(MAX_CAST)
]
actors = [
    {
        "ID": ids[i],
        "FIRST_NAME": " ".join(cast["name"].split(" ")[:-1]),
        "LAST_NAME": cast["name"].split(" ")[-1]
    }
    for i, cast in enumerate(movie["cast"][:MAX_CAST])
]
ids = [
    uuid.uuid4().int & (1 << 64)-1
    for _ in np.arange(MAX_WRITER)
]
writers = [
    {
        "ID": ids[i],
        "FIRST_NAME": " ".join(writer["name"].split(" ")[:-1]),
        "LAST_NAME": writer["name"].split(" ")[-1]
    }
    for i, writer in enumerate(movie["writer"][:MAX_WRITER])
]
ids = [
    uuid.uuid4().int & (1 << 64)-1
    for _ in np.arange(MAX_DIRECTOR)
]
directors = [
    {
        "ID": ids[i],
        "FIRST_NAME": " ".join(director["name"].split(" ")[:-1]),
        "LAST_NAME": director["name"].split(" ")[-1]
    }
    for i, director in enumerate(movie["director"][:MAX_DIRECTOR])
]

engine = _create_engine()
with engine.connect() as conn:
    people = [
        {
            **actor,
            **get_person_if_exists(conn, FIRST_NAME=actor["FIRST_NAME"], LAST_NAME=actor["LAST_NAME"]),
            "ROLES": [
                get_id(conn, "ROLES", "Actor"),
                *([] if actor not in writers else [get_id(conn, "ROLES", "Writer")]),
                *([] if actor not in directors else [get_id(conn, "ROLES", "Director")])
            ]
        }
        for actor in actors
    ]
    people += [
        {
            **writer,
            **get_person_if_exists(conn, FIRST_NAME=writer["FIRST_NAME"], LAST_NAME=writer["LAST_NAME"]),
            "ROLES": [
                get_id(conn, "ROLES", "Writer"),
                *([] if writer not in directors else [get_id(conn, "ROLES", "Director")])
            ]
        }
        for writer in writers
        if writer not in actors
    ]
    people += [
        {
            **director,
            **get_person_if_exists(conn, FIRST_NAME=writer["FIRST_NAME"], LAST_NAME=writer["LAST_NAME"]),
            "ROLES": [
                get_id(conn, "ROLES", "Writer"),
                *([] if writer not in directors else [get_id(conn, "ROLES", "Director")])
            ]
        }
        for director in directors
        if director not in actors and director not in writers
    ]
characters = [
    {
        "FIRST_NAME": " ".join(cast.currentRole["name"].split(" ")[:-1]),
        "LAST_NAME": cast["name"].split(" ")[-1],
        "ACTOR": people[i]["ID"]
    }
    for i, cast in enumerate(movie["cast"])
]
# currentRole
# name


# plot, synopsis
# %%
# from google_images_download import google_images_download


# Entire html page
html = wikipedia.page("when night is falling (film)").html()
page = BeautifulSoup(html, 'html.parser')
# %%
[person.text.split(" as ") for person in page.find("span", {"class": "mw-headline", "id": "Cast"}).parent.find_next_sibling(
    "ul"
).find_all("li")]

# %%

movies = [
    "Ammonite",
    "Drool",
    "The purple sea",
    "When night is falling",
    "Jenny's Wedding",
    "Gia",
    "But I'm a Cheerleader"
]
# for idx in range(len(movies)):
#   movie = movies[idx]

#   suggestions = wikipedia.search(movie, results=5)
#   print(suggestions)

#   suggestions = wikipedia.search(movie + " (film)", results=5)
#   print(suggestions)

movie = movies[4]

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
# %%


def get_wikipedia_info(movie_title):
    info = {}

    search_term = movie_title + " (film)"
    info["summary"] = wikipedia.summary(search_term)
    info["year"] = re.findall(r'[0-9]{4}', summary)[0]
    info["url"] = wikipedia.page(search_term).url

    # Entire html page
    html = wikipedia.page(search_term).html()
    page = BeautifulSoup(html, 'html.parser')


# %%
url = wikipedia.page(movie).url
print(url)
# %%
html = wikipedia.page(movie).html()
page = BeautifulSoup(html, 'html.parser')

# %%
page.find("h2", string="Cast").find_next_sibling(
    "ul"
).findall("li")
# print(page.prettify())
# %%
# p
# .infobox


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
    return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url, None, header)), 'html.parser')


query = "But Im a Cheerleader"
image_type = "ActiOn"
query = query.split()
query = '+'.join(query)
url = "https://www.google.com/search?q=" + query + "&source=lnms&tbm=isch"

# add the directory for your image here
header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
}
soup = get_soup(url, header)

images = []  # contains the link for Large original images, type of  image
for img in soup.find_all("img", {"class": "yWs4tf"}):
    # link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
    # ActualImages.append((link, Type))
    images.append(img["src"])
print(images)


# %%
os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, "images")
output_dir = os.path.join(pathlib.Path(
    __file__).parent.parent.absolute(), "images")
print(output_dir)


# %%
config = dict(
    limit=5,
    keywords="balloons",
    # image_directory,
    output_directory=output_dir,
    print_urls=True,

    # format = gif,
)

response = google_images_download.googleimagesdownload()
absolute_image_paths = response.download(config)

# %%
