"""Scrape movie information from wikipedia."""
from typing import Dict

from bs4 import BeautifulSoup
from IPython.display import display, HTML
import json
import pandas as pd

import re
import requests
import wikipedia
from googlesearch import search
import urllib

infobox_properties = [
    "Based on",
    "Release date",
    "Running time",
    "Country",
    "Language"
]

CONFIG = {
    "MAX_CHARACTERS": 5
}

#    "Starring",
# "Directed by",
# "Written by",


def get_infobox_property(page, property):
    """ Get information from wikipedia infobox"""
    infobox = page.find("table", {"class": "infobox"})
    found = infobox.find("th", string=property)
    if found is not None:
        val = found.find_next_siblings("td")
        if len(val) > 0:
            return val[0].text
    return ""


def map_value(key, val):
    return val


NAME_MAP = {
    "RUNNING_TIME": "RUNTIME"
}


def scrape_wikipedia_movie(movie_title: str) -> Dict:
    """Search movie title on wikipedia."""
    movie = {}

    search_term = movie_title + " (film)"
    movie["SUMMARY"] = wikipedia.summary(search_term)
    movie["YEAR"] = re.findall(r'[0-9]{4}', movie["summary"])[0]
    movie["WIKI_URL"] = wikipedia.page(search_term).url

    # Entire html page
    html = wikipedia.page(search_term).html()
    page = BeautifulSoup(html, 'html.parser')

    # Get Movie Properties from infobox
    for prop in infobox_properties:
        prop_val = get_infobox_property(page, prop)
        if prop_val:
            key = prop.upper().replace(" ", "_")
            movie[NAME_MAP.get(key, key)] = map_value(key, prop_val)

    # Get list of characters
    # characters = page.find("span", {
    #                        "class": "mw-headline", "id": "Cast"}).parent.find_next_sibling("ul").findAll("li")

    # [c.text for c in characters]

    return movie
