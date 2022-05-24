""" Central Scraper. """
from typing import Dict

from qwatch.scrape.imdb_api import scrape_imdb_movie
from qwatch.scrape.wiki_api import scrape_wikipedia_movie


def scrape_movie_information(movie_title: str) -> Dict:
    """Scrape information about movie."""

    return {
        **scrape_imdb_movie(movie_title),
        **scrape_imdb_movie(movie_title),
    }
