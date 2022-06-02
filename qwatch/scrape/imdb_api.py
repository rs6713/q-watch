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

from qwatch.io.input import get_person_if_exists, get_id, _get_movie_properties
from qwatch.io import _create_engine

genre_mappings = {
    "History": "Period-Piece",
    "Horror": "Horror/Thriller",
    "Thriller": "Horror/Thriller",
}

logger = logging.getLogger(__name__)


def get_first_name(name: str):

    if len(name.split(" ")) == 1:
        return name

    return " ".join(name.split(" ")[:-1])


def get_last_name(name: str):

    if len(name.split(" ")) == 1:
        return ""

    return name.split(" ")[-1]


class IMDBScraper(object):
    MAX_QUOTES = 10
    MAX_CAST = 5
    MAX_WRITER = 3
    MAX_DIRECTOR = 3

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        # executable_path param is not needed if you updated PATH
        self.browser = webdriver.Chrome(
            options=options,
            executable_path='E:/Projects/scraping/chromedriver_new.exe'
        )

        self.cinema_goer = Cinemagoer()

    def search(self, movie_title: str, year: int = None):
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
            self.movie_properties = self.cinema_goer.get_movie(self.movie_id)
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
            genres = _get_movie_properties(conn, "GENRE")

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
            return {}

        return {
            "SUMMARY": self.movie_properties.get("plot outline", None),
            "CERTIFICATE": ",".join(self.movie_properties["certificates"]),
            "LANGUAGE": ", ".join([lc.upper() for lc in self.movie_properties["language codes"]]),
            "GENRES": self.get_genres(),
            **self.get_box_office(),
            "RUNNING_TIME": self.movie_properties.get("runtimes", [None])[0],
            "YEAR": self.movie_properties.get("year", None),
            "TITLE": self.movie_properties.get("original title", None),
            "COUNTRY": self.movie_properties.get("countries", [None])[0],
            "BIO": self.get_bio(),
            **self.get_people(),
            "QUOTES": self.get_quotes(),
            "SOURCES": self.get_sources(),
            "URLS": [
                self.movie_url
            ]
        }

    def get_bio(self):
        tagline_section = self.movie_soup.find(
            "li", {"data-testid": "storyline-taglines"})
        tagline = (
            tagline_section.find("div").text
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
                if b.find("span").text in ["Gross worldwide", "Cumulative Worldwide Gross"]
            ]
            if len(box_offices):
                box_office = box_offices[0]

            budgets = [
                b.find("div").text
                for b in box_office_section.find_all("li")
                if b.find("span").text in ["Budget"]
            ]
            if len(budgets):
                budget = budgets[0]

        return {
            "BUDGET": budget,
            "BOX_OFFICE": box_office
        }

    def get_quotes(self):
        """ Get quotes from imdb quotes page. Try match back to recorded characters."""
        character_names = {
            F'{c["FIRST_NAME"]} {c["LAST_NAME"]}': c["ID"]
            for c in self.characters
        }

        quotes = self.quotes_soup.find("div", id="quotes_content"
                                       ).find_all("div", {"class": "quote"})
        quotes = [
            {
                "QUOTE_ID": i,
                "CHARACTER_ID": par.text.split(":", 1)[0][1:],
                "QUOTE": par.text.split(":", 1)[1][1:],
            }
            for i, quote in enumerate(quotes[:self.MAX_QUOTES])
            for par in quote.find_all("p")
            if len(par.text.split(":")) > 1
        ]
        logger.debug("Found %d quotes", len(quotes))
        if not len(quotes):
            return []

        quotes = [
            {
                **quote,
                "CHARACTER_ID": character_names[[name for name in character_names.keys() if quote["CHARACTER_ID"] in name][0]] if any([name for name in character_names.keys() if quote["CHARACTER_ID"] in name]) else None
            }
            for quote in quotes
        ]
        return pd.DataFrame(quotes)

    def get_sources(self):
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

        netflix = "Netflix" in self.movie_soup.find(
            "li", {"data-testid": "title-details-companies"}).text
        logger.debug("Available on netflix? %s", str(netflix))

        if len(prime_costs) == 0 and not netflix:
            return None

        # Get source details for amazon/netflix
        engine = _create_engine()
        with engine.connect() as conn:
            all_sources = _get_movie_properties(
                conn, "SOURCE", None, ["COST", "MEMBERSHIP_INCLUDED"])

        sources = pd.DataFrame([], columns=all_sources.columns)

        if netflix:
            netflix_source = all_sources[
                (all_sources.LABEL == "Netflix") & (all_sources.REGION == "UK")
            ].iloc[0, :]
            netflix_source.COST = 0.0
            netflix_source.MEMBERSHIP_INCLUDED = True
            sources = pd.concat(
                [sources, netflix_source.to_frame().T], axis=0, ignore_index=True)

        if len(prime_costs):
            prime_source = all_sources[
                (all_sources.LABEL == "Amazon Prime") & (
                    all_sources.REGION == "UK")
            ].iloc[0, :]
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

            return get_first_name(member.currentRole["name"]) in plot

        return [
            member for i, member in enumerate(cast)
            if i < self.MAX_CAST or override(member)
        ]

    def get_people(self):
        """Get the actors, characters, writers, directors."""
        engine = _create_engine()
        actor_id = None
        with engine.connect() as conn:
            role_members = {
                get_id(conn, "ROLES", "Actor"): self.clip_cast(self.movie_properties["cast"]),
                get_id(conn, "ROLES", "Director"): self.movie_properties["writer"][: self.MAX_WRITER],
                get_id(conn, "ROLES", "Writer"): self.movie_properties["director"][: self.MAX_DIRECTOR]
            }
            actor_id = get_id(conn, "ROLES", "Actor")

        people = []
        for role, members in role_members.items():
            people += [
                {
                    "ID": uuid.uuid4().int & (1 << 64)-1,
                    "FIRST_NAME": get_first_name(member["name"]),
                    "LAST_NAME": get_last_name(member["name"]),
                    "ROLE": role
                }
                for i, member in enumerate(members)
                if member.get("name", False)
            ]

        people = pd.DataFrame(people).groupby(["FIRST_NAME", "LAST_NAME"]).agg(
            {"ID": "first", "ROLE": list}).reset_index()

        with engine.connect() as conn:
            people = pd.DataFrame([{
                **person,
                **get_person_if_exists(conn, FIRST_NAME=person["FIRST_NAME"], LAST_NAME=person["LAST_NAME"]),
            } for person in people.to_dict("records")])

        # Get characters - after processing people for db matches
        characters = [
            {
                "ID": uuid.uuid4().int & (1 << 64)-1,
                "FIRST_NAME": get_first_name(cast.currentRole["name"]),
                "LAST_NAME": get_last_name(cast.currentRole["name"]),
                "ACTOR_ID": people[(people.FIRST_NAME + " " + people.LAST_NAME) == cast["name"]].iloc[0]["ID"]
            }
            for i, cast in enumerate(role_members[actor_id])
        ]
        self.characters = characters
        logger.debug(f"Characters:\n{characters}")

        return {
            "CHARACTERS": pd.DataFrame(characters),
            "PEOPLE": people,
        }

        # movie_cast = self.movie_properties["cast"][: self.MAX_CAST]
        # movie_writers = self.movie_properties["writer"][: self.MAX_WRITER]
        # movie_directors = self.movie_properties["director"][: self.MAX_DIRECTOR]

        # # Actors
        # actors = [
        #     {
        #         "ID": uuid.uuid4().int & (1 << 64)-1,
        #         "FIRST_NAME": " ".join(cast["name"].split(" ")[:-1]),
        #         "LAST_NAME": cast["name"].split(" ")[-1]
        #     }
        #     for i, cast in enumerate(movie_cast)
        #     if cast.get("name", False)
        # ]
        # logger.debug(f"Actors: \n{actors}")

        # # Writers
        # writers = [
        #     {
        #         "ID": uuid.uuid4().int & (1 << 64)-1,
        #         "FIRST_NAME": " ".join(writer["name"].split(" ")[:-1]),
        #         "LAST_NAME": writer["name"].split(" ")[-1]
        #     }
        #     for i, writer in enumerate(movie_writers)
        #     if writer.get("name", False)
        # ]
        # logger.debug(f"Writers:\n{writers}")

        # # Directors
        # directors = [
        #     {
        #         "ID": uuid.uuid4().int & (1 << 64)-1,
        #         "FIRST_NAME": " ".join(director["name"].split(" ")[:-1]),
        #         "LAST_NAME": director["name"].split(" ")[-1]
        #     }
        #     for i, director in enumerate(movie_directors)
        #     if director.get("name", False)
        # ]
        # logger.debug(f"Directors:\n{directors}")

        # def person_in(person, lst):
        #     members = [a["FIRST_NAME"] + a["LAST_NAME"] for a in lst]
        #     return (person["FIRST_NAME"] + person["LAST_NAME"]) in members

        # ###############################################################
        # # Check if person exists in db, if so load their information
        # ###############################################################
        # engine = _create_engine()
        # with engine.connect() as conn:
        #     people = [
        #         {
        #             **actor,
        #             **get_person_if_exists(conn, FIRST_NAME=actor["FIRST_NAME"], LAST_NAME=actor["LAST_NAME"]),
        #             "ROLE": [
        #                 get_id(conn, "ROLES", "Actor"),
        #                 *([] if not person_in(actor, writers)
        #                   else [get_id(conn, "ROLES", "Writer")]),
        #                 *([] if not person_in(actor, directors) else [get_id(conn, "ROLES", "Director")])
        #             ]
        #         }
        #         for actor in actors
        #     ]
        #     logger.debug(f"Actors: \n{people}")
        #     people += [
        #         {
        #             **writer,
        #             **get_person_if_exists(conn, FIRST_NAME=writer["FIRST_NAME"], LAST_NAME=writer["LAST_NAME"]),
        #             "ROLE": [
        #                 get_id(conn, "ROLES", "Writer"),
        #                 *([] if not person_in(writer, directors) else [get_id(conn, "ROLES", "Director")])
        #             ]
        #         }
        #         for writer in writers
        #         if not person_in(writer, actors)
        #     ]
        #     people += [
        #         {
        #             **director,
        #             **get_person_if_exists(conn, FIRST_NAME=director["FIRST_NAME"], LAST_NAME=director["LAST_NAME"]),
        #             "ROLE": [
        #                 get_id(conn, "ROLES", "Director"),
        #             ]
        #         }
        #         for director in directors
        #         if not person_in(director, actors) and not person_in(director, writers)
        #     ]

        # # Get characters - after processing people for db matches
        # characters = [
        #     {
        #         "ID": uuid.uuid4().int & (1 << 64)-1,
        #         "FIRST_NAME": " ".join(cast.currentRole["name"].split(" ")[:-1]),
        #         "LAST_NAME": cast.currentRole["name"].split(" ")[-1],
        #         "ACTOR_ID": people[i]["ID"]
        #     }
        #     for i, cast in enumerate(movie_cast)
        # ]
        # logger.debug(f"Characters:\n{characters}")

        # return {
        #     "CHARACTERS": pd.DataFrame(characters),
        #     "PEOPLE": pd.DataFrame(people),
        # }


# def get_imdb_movie(movie_id):
#     # Get movie imdb page
#     url = f"https://www.imdb.com/title/tt{movie_id}"
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     # executable_path param is not needed if you updated PATH
#     browser = webdriver.Chrome(
#         options=options, executable_path='E:/Projects/scraping/chromedriver_new.exe')
#     browser.get(url)
#     html = browser.page_source
#     soup = BeautifulSoup(html, "html.parser")

#     ##########################################
#     # Box office, Budget
#     ##########################################
#     box_office_box = soup.find(
#         "div", {
#             "data-testid": "title-boxoffice-section"
#         }).find_all(
#         "li"
#     ) if soup.find("div", {"data-testid": "title-boxoffice-section"}) is not None else []
#     box_offices = [
#         b.find("div").text
#         for b in box_office_box
#         if b.find("span").text in ["Gross worldwide", "Cumulative Worldwide Gross"]
#     ]
#     logger.debug(f"Box office: {box_offices}")

#     budget = [
#         b.find("div").text
#         for b in box_office_box
#         if b.find("span").text in ["Budget"]
#     ]
#     logger.debug(f"Budget: {budget}")

#     taglines = (
#         soup.find("li", {"data-testid": "storyline-taglines"}).find("div").text
#         if soup.find("li", {"data-testid": "storyline-taglines"}) is not None else None
#     )
#     logger.debug(f"Taglines: {taglines}")

#     ###########################################
#     # Movie Sources (according to imdb)
#     ###########################################
#     prime = [
#         d.find_next_sibling("div").text
#         for d in soup.select('div:-soup-contains("Watch on Prime Video")') if hasattr(d, "find_next_sibling") and d.find_next_sibling("div") is not None
#     ]
#     prime_prices = [
#         p for p in prime
#         if "rent/buy" in p
#     ]
#     logger.debug(f"Prime Prices: {prime_prices}")

#     netflix = "Netflix" in soup.find(
#         "li", {"data-testid": "title-details-companies"}).text
#     logger.debug("Available on netflix? %s", str(netflix))

#     #####################################
#     # Quotes
#     #####################################
#     MAX_QUOTES = 10
#     site = requests.get(
#         f"https://www.imdb.com/title/tt{movie_id}/quotes")
#     soup = BeautifulSoup(site.text, "html.parser")
#     quotes = soup.find("div", id="quotes_content").find_all(
#         "div", {"class": "quote"})
#     quotes = [
#         list(zip(
#             [par.text.split(":", 1)[0][1:] for par in quote.find_all(
#                 "p") if len(par.text.split(":")) > 1],
#             [par.text.split(":", 1)[1][1:] for par in quote.find_all(
#                 "p") if len(par.text.split(":")) > 1]
#         ))
#         for quote in quotes[:MAX_QUOTES]
#     ]
#     logger.debug("Found %d quotes", len(quotes))

#     return {
#         "QUOTES": quotes,
#         "BOX_OFFICE":
#         "BUDGET":
#         "SOURCES": sources
#     }


# def scrape_imdb_movie(movie_title: str) -> Dict:
#     """Scrape movie information from imdb."""
#     ia = Cinemagoer()
#     movies = ia.search_movie(movie_title)

#     scraped_movie_info = get_imdb_movie(movies[0].movieID)

#     if len(movies) == 0:
#         return {}

#     movie = ia.get_movie(movies[0].movieID)

#     # Convert imdb genres to ids
#     engine = _create_engine()
#     with engine.connect() as conn:
#         movie["genres"] = pd.DataFrame([
#             [get_id(conn, "GENRES", genre_mappings.get(g, g))]
#             for g in movie.get("genres", [])
#         ], columns=["ID"])

#     ############################################
#     # Movie Details
#     ############################################
#     info = {
#         "SUMMARY": movie.get("plot outline", None),
#         "CERTIFICATE": ",".join(movie["certificates"]),
#         "LANGUAGE": ", ".join([lc.upper() for lc in movie["language codes"]]),
#         "GENRES": movie["genres"],
#         "BUDGET": movie.get("box office", {}).get("Budget", None),
#         "BOX_OFFICE": movie.get("box office", {}).get("Cumulative Worldwide Gross", None),
#         "RUNNING_TIME": movie.get("runtimes", [None])[0],
#         "YEAR": movie.get("year", None),
#         "TITLE": movie.get("original title", None),
#         "COUNTRY": movie.get("countries", [None])[0],
#     }

#     #########################################
#     # Actors, Characters, Writers, Directors
#     #########################################
#     cast = movie["cast"]
#     MAX_CAST = 5
#     MAX_WRITER = 3
#     MAX_DIRECTOR = 3
#     # Actors
#     ids = [
#         uuid.uuid4().int & (1 << 64)-1
#         for _ in np.arange(MAX_CAST)
#     ]
#     actors = [
#         {
#             "ID": ids[i],
#             "FIRST_NAME": " ".join(cast["name"].split(" ")[:-1]),
#             "LAST_NAME": cast["name"].split(" ")[-1]
#         }
#         for i, cast in enumerate(movie["cast"][:MAX_CAST])
#     ]
#     logger.debug(f"Actors: \n{actors}")
#     # Writers
#     ids = [
#         uuid.uuid4().int & (1 << 64)-1
#         for _ in np.arange(MAX_WRITER)
#     ]
#     logger.debug(f"Raw writers: \n {movie['writer']}")
#     writers = [
#         {
#             "ID": ids[i],
#             "FIRST_NAME": " ".join(writer["name"].split(" ")[:-1]),
#             "LAST_NAME": writer["name"].split(" ")[-1]
#         }
#         for i, writer in enumerate(movie["writer"][:MAX_WRITER])
#         if writer.get("name", False)
#     ]
#     logger.debug(f"Writers:\n{writers}")
#     # Directors
#     ids = [
#         uuid.uuid4().int & (1 << 64)-1
#         for _ in np.arange(MAX_DIRECTOR)
#     ]
#     logger.debug(f"Raw directors: \n {movie['director']}")
#     directors = [
#         {
#             "ID": ids[i],
#             "FIRST_NAME": " ".join(director["name"].split(" ")[:-1]),
#             "LAST_NAME": director["name"].split(" ")[-1]
#         }
#         for i, director in enumerate(movie["director"][:MAX_DIRECTOR])
#         if director.get("name", False)
#     ]
#     logger.debug(f"Directors:\n{directors}")

#     ###############################################################
#     # Check if person exists in db, if so load their information
#     ###############################################################
#     engine = _create_engine()
#     with engine.connect() as conn:
#         people = [
#             {
#                 **actor,
#                 **get_person_if_exists(conn, FIRST_NAME=actor["FIRST_NAME"], LAST_NAME=actor["LAST_NAME"]),
#                 "ROLE": [
#                     get_id(conn, "ROLES", "Actor"),
#                     *([] if (actor["FIRST_NAME"]+actor["LAST_NAME"] not in [a["FIRST_NAME"] +
#                       a["LAST_NAME"] for a in writers]) else [get_id(conn, "ROLES", "Writer")]),
#                     *([] if (actor["FIRST_NAME"]+actor["LAST_NAME"] not in [a["FIRST_NAME"]+a["LAST_NAME"] for a in directors]) else [get_id(conn, "ROLES", "Director")])
#                 ]
#             }
#             for actor in actors
#         ]
#         logger.debug(f"Actors: \n{people}")
#         people += [
#             {
#                 **writer,
#                 **get_person_if_exists(conn, FIRST_NAME=writer["FIRST_NAME"], LAST_NAME=writer["LAST_NAME"]),
#                 "ROLE": [
#                     get_id(conn, "ROLES", "Writer"),
#                     *([] if (writer["FIRST_NAME"]+writer["LAST_NAME"] not in [a["FIRST_NAME"]+a["LAST_NAME"] for a in directors]) else [get_id(conn, "ROLES", "Director")])
#                 ]
#             }
#             for writer in writers
#             if (writer["FIRST_NAME"]+writer["LAST_NAME"] not in [a["FIRST_NAME"]+a["LAST_NAME"] for a in actors])
#         ]
#         people += [
#             {
#                 **director,
#                 **get_person_if_exists(conn, FIRST_NAME=director["FIRST_NAME"], LAST_NAME=director["LAST_NAME"]),
#                 "ROLE": [
#                     get_id(conn, "ROLES", "Director"),
#                 ]
#             }
#             for director in directors
#             if (director["FIRST_NAME"]+director["LAST_NAME"] not in [a["FIRST_NAME"]+a["LAST_NAME"] for a in actors]) and (director["FIRST_NAME"]+director["LAST_NAME"] not in [a["FIRST_NAME"]+a["LAST_NAME"] for a in writers])
#         ]
#         ids = [
#             uuid.uuid4().int & (1 << 64)-1
#             for _ in np.arange(MAX_CAST)
#         ]
#         characters = [
#             {
#                 "ID": ids[i],
#                 "FIRST_NAME": " ".join(cast.currentRole["name"].split(" ")[:-1]),
#                 "LAST_NAME": cast.currentRole["name"].split(" ")[-1],
#                 "ACTOR_ID": people[i]["ID"]
#             }
#             for i, cast in enumerate(movie["cast"][:MAX_CAST])
#         ]
#         logger.debug(f"Characters:\n{characters}")

#     return {
#         #**info,
#         "CHARACTERS": pd.DataFrame(characters),
#         "PEOPLE": pd.DataFrame(people),
#     }
