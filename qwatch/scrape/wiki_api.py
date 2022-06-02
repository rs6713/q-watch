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


def map_value(key, val):
    return val


class WIKIScraper(object):
    MAX_CHARACTERS = 5

    def __init__(self):
        self.NAME_MAP = {
            "RUNNING_TIME": "RUNTIME"
        }

        self.infobox_properties = [
            "Based on",
            "Release date",
            "Running time",
            "Country",
            "Language"
        ]
        #    "Starring",
        # "Directed by",
        # "Written by",
        self.wiki_url = None

    def search(self, movie_title: str, year: int = None):
        self.wiki_url = None

        search_term = movie_title + \
            ("" if year is None else f" {year}") + " (film)"
        page = wikipedia.page(search_term)

        if not page:
            return

        self.wiki_url = page.url
        self.summary = wikipedia.summary(search_term)

        # Entire html page
        html = wikipedia.page(search_term).html()
        self.page = BeautifulSoup(html, 'html.parser')

    def scrape(self, movie_title: str, year: int = None):

        self.search(movie_title, year)

        if self.wiki_url is None:
            return {}

        return {
            "SUMMARY": self.summary,
            "YEAR": re.findall(r'[0-9]{4}', self.summary)[0] if year is None else year,
            "URLS": [
                self.wiki_url
            ],
            **self.get_movie_infobox_properties()
        }

    def get_movie_infobox_properties(self):
        movie = {}
        # Get Movie Properties from infobox
        for prop in self.infobox_properties:
            prop_val = self._get_infobox_property(prop)
            if prop_val:
                key = prop.upper().replace(" ", "_")
                movie[self.NAME_MAP.get(key, key)] = prop_val

        return movie

    def _get_infobox_property(self, property: str):
        """ Get information from wikipedia infobox"""
        infobox = self.page.find("table", {"class": "infobox"})
        found = infobox.find("th", string=property)
        if found is not None:
            val = found.find_next_siblings("td")
            if len(val) > 0:
                return val[0].text
        return ""


# def scrape_wikipedia_movie(movie_title: str) -> Dict:
#     """Search movie title on wikipedia."""
#     movie = {}

#     search_term = movie_title + " (film)"
#     movie["SUMMARY"] = wikipedia.summary(search_term)
#     movie["YEAR"] = re.findall(r'[0-9]{4}', movie["summary"])[0]
#     movie["WIKI_URL"] = wikipedia.page(search_term).url

#     # Entire html page
#     html = wikipedia.page(search_term).html()
#     page = BeautifulSoup(html, 'html.parser')

#     # Get Movie Properties from infobox
#     for prop in infobox_properties:
#         prop_val = get_infobox_property(page, prop)
#         if prop_val:
#             key = prop.upper().replace(" ", "_")
#             movie[NAME_MAP.get(key, key)] = map_value(key, prop_val)

#     # Get list of characters
#     # characters = page.find("span", {
#     #                        "class": "mw-headline", "id": "Cast"}).parent.find_next_sibling("ul").findAll("li")

#     # [c.text for c in characters]

#     return movie
