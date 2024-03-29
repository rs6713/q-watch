"""Scrape movie information from wikipedia."""
import logging
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

logger = logging.getLogger(__name__)


class WIKIScraper(object):

    def __init__(self, options=None):
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
        # "Starring",
        # "Directed by",
        # "Written by",
        self.wiki_url = None
        self.options = options

    def search(self, movie_title: str, year: int = None):
        logger.info("Performing Wiki Search for %s year %s",
                    movie_title, str(year))
        self.wiki_url = None

        search_term = movie_title + \
            ("" if year is None else f" {year}") + " (film)"

        try:
            page = wikipedia.page(search_term)
        # Throw PageError when no match found
        except Exception as _:
            return

        self.wiki_url = page.url
        self.summary = wikipedia.summary(search_term)

        # Entire html page
        html = wikipedia.page(search_term).html()
        self.page = BeautifulSoup(html, 'html.parser')

    def scrape(self, movie_title: str, year: int = None):

        self.search(movie_title, year)

        if self.wiki_url is None:
            logger.warning(
                "No matches were found in Wiki for: %s, %s",
                movie_title, str(year)
            )
            return {}

        return {
            "SUMMARY": self.summary,
            "YEAR": re.findall(r'[0-9]{4}', self.summary)[0] if year is None else year,
            "URLS": [
                self.wiki_url
            ],
            **self.get_movie_infobox_properties(),
            "PEOPLE": (self.get_people() if self.options['FETCH_PEOPLE'].get() else None)
        }

    def get_people(self):
        try:
            return [person.text.lower().split(" as ") for person in self.page.find("span", {"class": "mw-headline", "id": "Cast"}).parent.find_next_sibling(
                "ul"
            ).find_all("li") if " as " in person]
        except Exception as e:
            logger.warning(e)
            logger.warning("No characters found in wiki page")
            return None

    def get_movie_infobox_properties(self):
        movie = {}
        # Get Movie Properties from infobox
        for prop in self.infobox_properties:
            prop_val = self._get_infobox_property(prop)
            if prop_val:
                key = prop.upper().replace(" ", "_")

                if self.NAME_MAP.get(key, key) == 'RUNTIME':
                    prop_val = prop_val.split(' minutes')[0]
                movie[self.NAME_MAP.get(key, key)] = prop_val

        return movie

    def _get_infobox_property(self, property: str):
        """ Get information from wikipedia infobox"""
        infobox = self.page.find("table", {"class": "infobox"})
        if infobox is not None:
            found = infobox.find("th", string=property)
            if found is not None:
                val = found.find_next_siblings("td")
                if len(val) > 0:
                    return val[0].text
        return ""
