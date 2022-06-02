# %%
from selenium.webdriver.common.keys import Keys
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

from qwatch.scrape import IMDBScraper, WIKIScraper
from qwatch.scrape import scrape_movie_information

# %%
scrape_movie_information("but im a cheerleader", 1999, True)

# %%
s = WIKIScraper()
s.scrape("but im a cheerleader", 1999)

# %%
scraper = IMDBScraper()
res = scraper.scrape("but im a cheerleader", 1999)

# %%
#options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     # executable_path param is not needed if you updated PATH
#     browser = webdriver.Chrome(
#         options=options, executable_path='E:/Projects/scraping/chromedriver_new.exe')

driver = webdriver.Chrome(
    executable_path='E:/Projects/scraping/chromedriver_new.exe')
driver.get("https://www.python.org")

driver.execute_script(
    "window.open('about:blank', 'secondtab');"
)
driver.switch_to.window("secondtab")
driver.get("https://www.netflix.com")

# %%
