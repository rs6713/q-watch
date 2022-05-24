""" Scrape Movie Information using IMDB Database."""
import json
import logging
import os
import pathlib
import re
import requests
from typing import Dict, List
import urllib
import uuid

from bs4 import BeautifulSoup
from imdb import Cinemagoer
from IPython.display import display, HTML
import numpy as np
import pandas as pd

from qwatch.io.input import get_actor_ids, get_person_if_exists, get_id
from qwatch.io import _create_engine

genre_mappings = {
    "History": "Period-Piece",
    "Horror": "Horror/Thriller",
    "Thriller": "Horror/Thriller",
}

logger = logging.getLogger(__name__)


def scrape_imdb_movie(movie_title: str) -> Dict:
    """Scrape movie information from imdb."""
    ia = Cinemagoer()

    movies = ia.search_movie(movie_title)

    if len(movies) == 0:
        return {}

    movie = ia.get_movie(movies[0].movieID)

    engine = _create_engine()
    with engine.connect() as conn:
        movie["genres"] = pd.DataFrame([
            [get_id(conn, "GENRES", genre_mappings.get(g, g))]
            for g in movie.get("genres", [])
        ], columns=["ID"])

    ############################################
    # Movie Details
    ############################################
    info = {
        "SUMMARY": movie.get("plot outline", None),
        "CERTIFICATE": ",".join(movie["certificates"]),
        "LANGUAGE": ", ".join([lc.upper() for lc in movie["language codes"]]),
        "GENRES": movie["genres"],
        "BUDGET": movie.get("box office", {}).get("Budget", None),
        "BOX_OFFICE": movie.get("box office", {}).get("Cumulative Worldwide Gross", None),
        "RUNNING_TIME": movie.get("runtimes", [None])[0],
        "YEAR": movie.get("year", None),
        "TITLE": movie.get("original title", None),
        "COUNTRY": movie.get("countries", [None])[0],
    }

    #########################################
    # Actors, Characters, Writers, Directors
    #########################################
    cast = movie["cast"]
    MAX_CAST = 5
    MAX_WRITER = 3
    MAX_DIRECTOR = 3
    # Actors
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
    logger.debug(f"Actors: \n{actors}")
    # Writers
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
    logger.debug(f"Writers:\n{writers}")
    # Directors
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
    logger.debug(f"Directors:\n{directors}")

    ###############################################################
    # Check if person exists in db, if so load their information
    ###############################################################
    engine = _create_engine()
    with engine.connect() as conn:
        people = [
            {
                **actor,
                **get_person_if_exists(conn, FIRST_NAME=actor["FIRST_NAME"], LAST_NAME=actor["LAST_NAME"]),
                "ROLE": [
                    get_id(conn, "ROLES", "Actor"),
                    *([] if actor not in writers else [get_id(conn, "ROLES", "Writer")]),
                    *([] if actor not in directors else [get_id(conn, "ROLES", "Director")])
                ]
            }
            for actor in actors
        ]
        logger.debug(f"Actors: \n{people}")
        people += [
            {
                **writer,
                **get_person_if_exists(conn, FIRST_NAME=writer["FIRST_NAME"], LAST_NAME=writer["LAST_NAME"]),
                "ROLE": [
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
                **get_person_if_exists(conn, FIRST_NAME=director["FIRST_NAME"], LAST_NAME=director["LAST_NAME"]),
                "ROLE": [
                    get_id(conn, "ROLES", "Director"),
                ]
            }
            for director in directors
            if director not in actors and director not in writers
        ]
        ids = [
            uuid.uuid4().int & (1 << 64)-1
            for _ in np.arange(MAX_CAST)
        ]
        characters = [
            {
                "ID": ids[i],
                "FIRST_NAME": " ".join(cast.currentRole["name"].split(" ")[:-1]),
                "LAST_NAME": cast.currentRole["name"].split(" ")[-1],
                "ACTOR_ID": people[i]["ID"]
            }
            for i, cast in enumerate(movie["cast"][:MAX_CAST])
        ]
        logger.debug(f"Characters:\n{characters}")

    return {
        **info,
        "CHARACTERS": pd.DataFrame(characters),
        "PEOPLE": pd.DataFrame(people),
    }
