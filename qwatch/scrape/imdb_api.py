""" Scrape Movie Information using IMDB Database."""
import json
import logging
import os
import pathlib
import re
import requests
import time
from typing import Dict, List
import urllib
import uuid

from bs4 import BeautifulSoup
from imdb import Cinemagoer
from IPython.display import display, HTML
import numpy as np
import pandas as pd
from selenium import webdriver

from qwatch.io.input import get_person_if_exists, get_id, _get_movie_labels, get_entries
from qwatch.io import _create_engine
from qwatch.utils import get_first_name, get_last_name

genre_mappings = {
    "History": "Period-Piece",
    "Horror": "Horror/Thriller",
    "Thriller": "Horror/Thriller",
}

logger = logging.getLogger(__name__)


class IMDBScraper(object):
    NUM_QUOTES_SCRAPE = 10
    NUM_CAST_SCRAPE = 5
    NUM_WRITER_SCRAPE = 3
    NUM_DIRECTOR_SCRAPE = 3

    def __init__(self, options=None):
        if options is not None:
            for option, var in options.items():
                logger.debug(
                    "Configuring %s with %d",
                    option, int(var.get())
                )
                setattr(self, option, int(var.get()))

        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # executable_path param is not needed if you updated PATH
        self.browser = webdriver.Chrome(
            options=options,
            executable_path='E:/Projects/scraping/chromedriver.exe'
        )

        self.cinema_goer = Cinemagoer()

        engine = _create_engine()
        with engine.connect() as conn:
            self.known_actors, _ = get_entries(conn, "PEOPLE", return_properties=[
                'FIRST_NAME', 'LAST_NAME'])
            self.known_actors = [
                a['FIRST_NAME'] + ' ' + a['LAST_NAME']
                for a in self.known_actors
            ]
            logger.debug('Known Actors %d: %s', len(
                self.known_actors), str(self.known_actors[:5]))

    def search(self, movie_title: str, year: int = None):
        logger.info("Performing IMDB Search for %s year %s",
                    movie_title, str(year))
        self.movie_properties = {}
        movies = self.cinema_goer.search_movie(movie_title)

        logger.debug("Found %d matching movie titles to %s",
                     len(movies), movie_title)

        if year is None:
            self.movie_id = movies[0].movieID if len(movies) else None
        else:
            logger.debug("Only selecting movies with year: %d", year)
            year_movies = [
                movie for movie in movies if movie.get("year", None) == year
            ]
            self.movie_id = year_movies[0].movieID if len(
                year_movies) else None

        if self.movie_id is not None:
            self.movie_properties = self.cinema_goer.get_movie(
                self.movie_id,
                ['main', 'plot', 'synopsis', 'taglines']
            )
            logging.debug("Selected %s", str(movies[0]))

            # Get IMDB Main page
            self.movie_url = f"https://www.imdb.com/title/tt{self.movie_id}"
            self.browser.get(self.movie_url)
            self.movie_soup = BeautifulSoup(
                self.browser.page_source, "html.parser")

            time.sleep(0.1)
            # Get IMDB Quotes Page
            site = requests.get(
                f"https://www.imdb.com/title/tt{self.movie_id}/quotes"
            )
            self.quotes_soup = BeautifulSoup(site.text, "html.parser")

    def get_genres(self):
        # Convert imdb genres to ids
        engine = _create_engine()
        with engine.connect() as conn:
            genres = _get_movie_labels(conn, "GENRE")

            return genres[
                genres.LABEL.isin([
                    genre_mappings.get(g, g)
                    for g in self.movie_properties.get("genres", [])
                ])
            ]
            # return pd.DataFrame([
            #     [get_id(conn, "GENRES", genre_mappings.get(g, g))]
            #     for g in self.movie_properties.get("genres", [])
            # ], columns=["ID"])

    def scrape(self, movie_title: str, year: int = None):
        self.search(movie_title, year)

        if self.movie_id is None:
            logger.warning(
                "No matches were found in IMDB for: %s, %s",
                movie_title, str(year)
            )
            return {}

        return {
            "SUMMARY": self.movie_properties.get("plot outline", None),
            "CERTIFICATE": ",".join(self.movie_properties.get("certificates", [])),
            "LANGUAGE": ", ".join([lc.upper() for lc in self.movie_properties.get("language codes", [])]),
            "GENRES": self.get_genres(),
            **self.get_box_office(),
            "RUNNING_TIME": self.movie_properties.get("runtimes", [''])[0].split(' minutes')[0],
            "YEAR": self.movie_properties.get("year", None) if year is None else year,
            "TITLE": self.movie_properties.get("original title", None),
            "COUNTRY": self.movie_properties.get("countries", [None])[0],
            "BIO": ((self.movie_properties['plot'][0] if len(self.movie_properties.get('plot', [])) else '') + (self.get_bio() or '')) or None,
            **(self.get_people() if self.FETCH_PEOPLE else {}),
            "QUOTES": self.get_quotes(),
            "SOURCES": self.get_sources(),
            'TAGLINES': '\n'.join(self.movie_properties.get('taglines', [])),
            "URLS": [
                self.movie_url
            ],
            'IMDB_ID': int(self.movie_id)
        }

    def get_bio(self):
        tagline_section = self.movie_soup.find(
            "li", {"data-testid": "storyline-taglines"})
        tagline = (
            tagline_section.find("label").text
            if tagline_section is not None else None
        )
        logger.debug("Tagline: %s", tagline)
        return tagline

    def get_box_office(self):
        box_office = self.movie_properties.get(
            "box office", {}).get("Cumulative Worldwide Gross", None)
        budget = self.movie_properties.get(
            "box office", {}).get("Budget", None)

        box_office_section = self.movie_soup.find(
            "div", {"data-testid": "title-boxoffice-section"})
        if box_office_section is not None:

            box_offices = [
                b.find("div").text
                for b in box_office_section.find_all("li")
                if b.find("button") and b.find('button').text in ["Gross worldwide", "Cumulative Worldwide Gross"]
            ]
            if len(box_offices):
                box_office = box_offices[0]

            budgets = [
                b.find("div").text
                for b in box_office_section.find_all("li")
                if b.find("button") and b.find('button').text in ["Budget"]
            ]
            if len(budgets):
                budget = budgets[0]

        return {
            "BUDGET": (budget or '').replace(' (estimated)', ''),
            "BOX_OFFICE": box_office
        }

    def get_quotes(self):
        """ Get quotes from imdb quotes page. Try match back to recorded characters."""
        character_names = {
            f'{c["FIRST_NAME"]} {c["LAST_NAME"]}': c["ID"]
            for c in getattr(self, 'characters', [])
        }

        quotes = self.quotes_soup.find("div", id="quotes_content"
                                       ).find_all("div", {"class": "quote"})
        quotes = [
            {
                "QUOTE_ID": i,
                "CHARACTER_ID": par.text.split(":", 1)[0][1:],
                "QUOTE": par.text.split(":", 1)[1][1:],
            }
            for i, quote in enumerate(quotes[:self.NUM_QUOTES_SCRAPE])
            for par in quote.find_all("p")
            if len(par.text.split(":")) > 1
        ]
        logger.debug("Found %d quotes", len(quotes))
        if not len(quotes):
            return None

        def find_character_id(name: str) -> int:
            nonlocal character_names

            def is_full_name(s: str):
                return len(s.split(" ")) > 1 and len(s.split(" ")[1]) > 0

            for c_name, c_id in character_names.items():

                # Quote has first/last name
                # Occurs when both full_names / first names only
                if c_name == name:
                    return c_id

                if is_full_name(c_name) and not is_full_name(name) and name.replace(" ", "") == c_name.split(" ")[0]:
                    return c_id

                if not is_full_name(c_name) and is_full_name(name) and name.split(" ")[0] == c_name.replace(" ", ""):
                    return c_id

            return -1  # Can't be none or converts col to float

        # If names match, give quotes correct character_id
        quotes = [
            {
                **quote,
                "CHARACTER_ID": find_character_id(quote["CHARACTER_ID"])
            }
            for quote in quotes
        ]
        return pd.DataFrame(quotes)

    def get_sources(self):
        bfi_source = len(self.movie_soup.select(
            'div:-soup-contains("Watch on BFI Player")')) > 0

        prime_container = self.movie_soup.select(
            'div:-soup-contains("Watch on Prime Video")')
        prime = [
            d.find_next_sibling("div").text
            for d in prime_container if hasattr(d, "find_next_sibling") and d.find_next_sibling("div") is not None
        ]
        prime_costs = [
            {"COST": float(re.findall(r'(?<=GBP)[0-9\.]+', p)[0])} if "rent/buy" in p
            else {"MEMBERSHIP_INCLUDED": True, "COST": None}
            for p in prime
            if "rent/buy" in p or p == "included with Prime"
        ]
        logger.debug(f"Prime Prices: {prime_costs}")

        if self.movie_soup.find(
            "li", {"data-testid": "title-details-companies"}
        ) is not None:
            netflix = "Netflix" in self.movie_soup.find(
                "li", {"data-testid": "title-details-companies"}
            ).text
            logger.debug("Available on netflix? %s", str(netflix))
        else:
            netflix = False

        if len(prime_costs) == 0 and not netflix and not bfi_source:
            return None

        # Get source details for amazon/netflix
        engine = _create_engine()
        with engine.connect() as conn:
            all_sources = _get_movie_labels(
                conn, "SOURCE", None, [])

        sources = pd.DataFrame(
            [], columns=["ID", "SOURCE_ID", "COST", "MEMBERSHIP_INCLUDED", "URL"])

        logger.info(f"BFI Source: {bfi_source}")
        if bfi_source:
            bfi_source_id = all_sources[
                (all_sources.LABEL == "British Film Institute") & (
                    all_sources.REGION == "UK")
            ].iloc[0, :].ID
            bfi_source = pd.Series([
                None, bfi_source_id, 0.0, True, ""
            ], index=["ID", "SOURCE_ID", "COST", "MEMBERSHIP_INCLUDED", "URL"])
            sources = pd.concat(
                [sources, bfi_source.to_frame().T], axis=0, ignore_index=True)

        if netflix:
            netflix_source_id = all_sources[
                (all_sources.LABEL == "Netflix") & (all_sources.REGION == "UK")
            ].iloc[0, :].ID
            netflix_source = pd.Series([
                None, netflix_source_id, 0.0, True, ""
            ], index=["ID", "SOURCE_ID", "COST", "MEMBERSHIP_INCLUDED", "URL"])
            sources = pd.concat(
                [sources, netflix_source.to_frame().T], axis=0, ignore_index=True)

        if len(prime_costs):
            prime_source_id = all_sources[
                (all_sources.LABEL == "Amazon Prime") & (
                    all_sources.REGION == "UK")
            ].iloc[0, :].ID
            prime_source = pd.Series(
                [None, prime_source_id, 0.0, False, ""],
                index=["ID", "SOURCE_ID", "COST", "MEMBERSHIP_INCLUDED", "URL"]
            )
            for prime in prime_costs:
                if prime.get("COST", False):
                    prime_source.COST = prime["COST"]
                if prime.get("MEMBERSHIP_INCLUDED", False):
                    prime_source.MEMBERSHIP_INCLUDED = True
            sources = pd.concat(
                [sources, prime_source.to_frame().T], axis=0, ignore_index=True)
        return sources

    def clip_cast(self, cast):
        """
        IMDB returns cast members sometimes unordered.

        This insists plot-relevant characters are kept.
        """
        def override(member):
            plot = self.movie_properties.get("plot outline", "")
            plot += ' '.join(self.movie_properties.get('synopsis', []))

            if member.get('name', -1) in self.known_actors:
                return True

            if "name" not in member.currentRole:
                return False

            return get_first_name(member.currentRole["name"]) in plot

        return [
            member for i, member in enumerate(cast)
            if i < self.NUM_CAST_SCRAPE or override(member)
        ]

    def get_people(self):
        """Get the actors, characters, writers, directors."""
        engine = _create_engine()
        actor_id = None
        with engine.connect() as conn:
            role_members = {
                get_id(conn, "ROLES", "Actor"): self.clip_cast(self.movie_properties.get("cast", [])),
                get_id(conn, "ROLES", "Director"): self.movie_properties.get("director", [])[: self.NUM_WRITER_SCRAPE],
                get_id(conn, "ROLES", "Writer"): self.movie_properties.get("writer", [])[: self.NUM_DIRECTOR_SCRAPE]
            }
            actor_id = get_id(conn, "ROLES", "Actor")

        people = []
        for role, members in role_members.items():
            for i, member in enumerate(members):
                if member.get('name', False):
                    member_props = {}
                    if member.__dict__.get('personID', False):
                        try:
                            member_props = self.cinema_goer.get_person(
                                str(member.__dict__['personID'])
                            )
                            member_props = {
                                'IMDB_ID': member_props['imdbID'],
                                'BIO': member_props['bio'],
                                'DOB': member_props['birth date'],
                                'HEADSHOT': member_props['headshot']
                            }
                            logger.info(
                                'Member props %s : %s',
                                member['name'], str(member_props)
                            )
                        except:
                            logger.warning(
                                'Failed to get Person %s from IMDB',
                                member.__dict__['personID']
                            )
                    else:
                        logger.info('Member %s has no imdb entry',
                                    member['name'])

                    people += [
                        {
                            "ID": uuid.uuid4().int & (1 << 64)-1,
                            "FIRST_NAME": get_first_name(member["name"]),
                            "LAST_NAME": get_last_name(member["name"]),
                            "ROLE": role,
                            **member_props
                        }
                    ]

        people = pd.DataFrame(people).groupby(["FIRST_NAME", "LAST_NAME"]).agg(
            {
                "ID": "first",
                "ROLE": list,
                'DOB': 'first',
                'BIO': 'first',
                'HEADSHOT': 'first',
                'IMDB_ID': 'first'
            }).reset_index()

        default_person = {
            "DISABILITY": [],
            "ETHNICITY": [],
            "GENDER": None,
            "DOB": "",
            "SEXUALITY": None,
            "BIO": "",
            "TRANSGENDER": None,
            'HEADSHOT': '',
            'NATIONALITY': '',
            'IMDB_ID': None,
        }
        with engine.connect() as conn:
            people = pd.DataFrame([{
                **default_person,
                **person,
                **get_person_if_exists(conn, FIRST_NAME=person["FIRST_NAME"], LAST_NAME=person["LAST_NAME"]),
            } for person in people.to_dict("records")])
            people = people.fillna(np.nan).replace([np.nan], [None])
            logger.debug(people)
        # Get characters - after processing people for db matches
        characters = [
            {
                "ID": uuid.uuid4().int & (1 << 64)-1,
                "FIRST_NAME": get_first_name(cast.currentRole["name"]),
                "LAST_NAME": get_last_name(cast.currentRole["name"]),
                "ACTOR_ID": people[(people.FIRST_NAME + " " + people.LAST_NAME) == cast["name"]].iloc[0]["ID"]
            }
            for i, cast in enumerate(role_members[actor_id])
            if "name" in cast.currentRole
        ]
        if len(characters) != len(role_members[actor_id]):
            logger.warning(
                "There are character references missing. %d Characters %d actors",
                len(characters), len(role_members[actor_id])
            )
        self.characters = characters
        logger.debug(f"Characters:\n{characters}")

        return {
            "CHARACTERS": pd.DataFrame(characters),
            "PEOPLE": people,
        }
