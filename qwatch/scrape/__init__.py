""" Central Scraper. """
import logging
import time
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

    # Use wiki people to order people from imdb
    if "PEOPLE" in wiki_information and wiki_information["PEOPLE"] is not None:
        actors = [p[0] for p in wiki_information["PEOPLE"]]
        characters = [p[1] for p in wiki_information["PEOPLE"]]

        imdb_information["CHARACTERS"].loc[:, "WEIGHT"] = imdb_information["CHARACTERS"].apply(
            lambda row: characters.index(
                f"{row.FIRST_NAME} {row.LAST_NAME}".lower()) if f"{row.FIRST_NAME} {row.LAST_NAME}".lower() in characters else 100,
            axis=1
        ).replace(-1, 100)
        imdb_information["CHARACTERS"].sort_values(
            by="WEIGHT", inplace=True, ascending=True)
        imdb_information["CHARACTERS"].drop(
            columns=["WEIGHT"], inplace=True)

        imdb_information["PEOPLE"].loc[:, "WEIGHT"] = imdb_information["PEOPLE"].apply(
            lambda row: actors.index(
                f"{row.FIRST_NAME} {row.LAST_NAME}".lower()) if f"{row.FIRST_NAME} {row.LAST_NAME}".lower() in actors else 100,
            axis=1
        ).replace(-1, 100)
        imdb_information["PEOPLE"].sort_values(
            by="WEIGHT", inplace=True, ascending=True)
        imdb_information["PEOPLE"].drop(columns=["WEIGHT"], inplace=True)

    #####################################################
    # Auto open tabs to further explore movie details
    #####################################################
    movie_query = '+'.join(movie_title.split(' ')) + \
        (('+' + str(year)) if year else '')
    yt_url = f"https://www.youtube.com/results?search_query={movie_query}+trailer"
    yt_full_url = f"https://www.youtube.com/results?search_query={movie_query}+full+movie"
    gsearch_url = f"https://www.google.com/search?q={movie_query}"

    urls = [
        yt_url,
        yt_full_url,
        gsearch_url,
        gsearch_url+"&tbm=isch",
        *wiki_information.get("URLS", []),
        #*imdb_information.get("URLS", []),
    ]

    ##################################################
    # (Optional) Open URL's in Chrome for quick review
    ##################################################
    if open_urls and len(urls):
        logger.info("Opening urls using chrome webdriver")
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(
            executable_path='E:/Projects/scraping/chromedriver_new.exe',
            options=options
        )
        driver.get(urls[0])
        for i, url in enumerate(urls[1:]):
            logger.info("Opening %s", url)
            driver.execute_script(
                f"window.open('about:blank', 'tab{i}');"
            )
            driver.switch_to.window(f"tab{i}")
            driver.get(url)
            time.sleep(0.1)
        driver.close()

    return {
        **{
            k: v for k, v in wiki_information.items()
            if v is not None and k != "URLS" and k != "PEOPLE"
        },
        ** {
            k: v for k, v in imdb_information.items()
            if v is not None and k != "URLS"
        }
    }
