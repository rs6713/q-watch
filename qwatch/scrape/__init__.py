""" Central Scraper. """
import logging
from typing import Dict

from selenium import webdriver

from qwatch.scrape.imdb_api import IMDBScraper
from qwatch.scrape.wiki_api import WIKIScraper

logger = logging.getLogger(__name__)


def scrape_movie_information(movie_title: str, year: str = None, open_urls=False, options=None) -> Dict:
    """Scrape information about movie."""
    imdb_scraper = IMDBScraper(options=options)
    wiki_scraper = WIKIScraper(options=options)

    logger.info(
        "Scraping Information for movie [%s] Year:%s", movie_title, str(year))
    imdb_information = imdb_scraper.scrape(movie_title, year)
    wiki_information = wiki_scraper.scrape(movie_title, year)

    #####################################################
    # Auto open tabs to further explore movie details
    #####################################################
    movie_query = '+'.join(movie_title.split(' ')) + \
        (('+' + str(year)) if year else '')
    yt_url = f"https://www.youtube.com/results?search_query={movie_query}+trailer"
    yt_full_url = f"https://www.youtube.com/results?search_query={movie_query}+full+movie"
    gsearch_url = f"https://www.google.com/search?q={movie_query}"

    urls = [
        yt_url, yt_full_url, gsearch_url, gsearch_url+"&tbm=isch",
        *wiki_information.get("URLS", []),
        *imdb_information.get("URLS", []),
    ]

    if open_urls and len(urls):
        driver = webdriver.Chrome(
            executable_path='E:/Projects/scraping/chromedriver_new.exe')
        driver.get(urls[0])
        for i, url in enumerate(urls[1:]):
            driver.execute_script(
                f"window.open('about:blank', 'tab{i}');"
            )
            driver.switch_to.window(f"tab{i}")
            driver.get(url)

    return {
        **{
            k: v for k, v in wiki_information.items()
            if v is not None and k != "URLS"
        },
        ** {
            k: v for k, v in imdb_information.items()
            if v is not None and k != "URLS"
        }
    }
