from bs4 import BeautifulSoup
from IPython.display import display, HTML
import json
import pandas as pd
import re
import requests
import wikipedia
from googlesearch import search
import urllib

properties = [
  "Directed by",
  "Written by",
  "Based on",
  "Starring",
  "Release date",
  "Running time",
  "Country",
  "Language"
]

def get_infobox_property(page, property):
  """ Get information from wikipedia infobox"""
  infobox = page.find("table", {"class": "infobox"})
  found = infobox.find("th", string=property)
  if found is not None:
    val = found.find_next_siblings("td")
    if len(val) > 0:
      return val[0].text
  return ""

def get_movie_details(movie_title):
  info = {}

  search_term = movie_title + " (film)"
  info["summary"] = wikipedia.summary(search_term)
  info["year"] = re.findall(r'[0-9]{4}', info["summary"])[0]
  info["url"] = wikipedia.page(search_term).url

  # Entire html page
  html = wikipedia.page(search_term).html()
  page = BeautifulSoup(html, 'html.parser')

  # Get Movie Properties from infobox
  for prop in properties:
    prop_val = get_infobox_property(page, prop)
    if prop_val:
      info[prop] = prop_val

  return info
