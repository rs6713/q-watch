""" Functions to retrieve data from SQL Server."""
from typing import Dict, List

import pandas as pd
from sqlalchemy import (
  case,
  create_engine,
  func, 
  MetaData,
  select,
  sql,
  Table,
  update
)
from sqlalchemy.engine import (
  Connection,
  Row,
  url,
  Engine
)

SCHEMA = "dbo"

def get_movies_ids(conn: Connection) -> List[Dict]:
  """ Retrieve Movie title, id list"""

  movie_table = Table("MOVIES", MetaData(), schema=SCHEMA, autoload_with=conn)
  query = select(
    movie_table.c.ID,
    movie_table.c.TITLE
  )

  columns = conn.execute(query).keys()
  results = {
    row._mapping["ID"]: row._mapping["TITLE"]
    for row in conn.execute(query).fetchall()
  }
  return results


def get_movies(conn: Connection, filters: Dict=None) -> List[Dict]:
  """Retrieve Movies that match filters."""
  meta = MetaData()
  pass

def get_movie(conn: Connection, movie_id: int) -> Dict:
  """Retrieve Movie by Id. """
  meta = MetaData()

  movie_table = Table("MOVIES", meta, schem=SCHEMA, autoload_with=conn)

  movie_quote_table = Table("MOVIE_QUOTE", meta, schema=SCHEMA, autoload_with=conn)

  movie_intensity_table = Table("MOVIE_INTENSITY", meta, schema=SCHEMA, autoload_with=conn)
  intensity_table = Table("INTENSITIES", meta, schema=SCHEMA, autoload_with=conn)

  ages_table = Table("AGES", meta, schema=SCHEMA, autoload_with=conn)

  movie_query = select(
    ages_table.c.LABEL.label("AGE"),
    movie_table.c.RUNTIME,
    movie_table.c.AGE_RATING,
    movie_table.c.LANGUAGE,
    movie_table.c.SUMMARY, 
    movie_table.c.BIO,
    movie_table.c.TITLE,
    movie_table.c.YEAR
  ).select_from(movie_table).join(
    ages_table, ages_table.c.ID == movie_table.c.AGE
  ).where(
    movie_table.c.ID == movie_id
  )

  quote_query = select(
    movie_quote_table.c.ID,
    movie_quote_table.c.QUOTE
  ).select_from(
    movie_quote_table
  ).where(
    movie_quote_table.c.MOVIE_ID==movie_id
  )

  # genre_query = select(
  #   genre_table.c.LABEL.label("GENRE")
  # ).select_from(
  #   movie_genre_table
  # ).join(
  #   genre_table, genre_table.c.ID == movie_genre_table.c.GENRE_ID
  # ).where(
  #   movie_genre_table.c.MOVIE_ID == movie_id
  # )
  genres = _get_movie_properties(conn, "GENRE", movie_id)
  representations = _get_movie_properties(conn, "REPRESENTATION", movie_id)
  tropes = _get_movie_properties(conn, "TROPE_TRIGGER", movie_id)



  #get_people(conn, movie_id)
  #get_images(conn, movie_id)

def get_people(conn: Connection, movie_id:int):
  """Get people associated with movie."""
  meta = MetaData()

  roles_table = Table("ROLES", meta, schema=SCHEMA, autoload_with=conn)
  genders_table = Table("GENDERS", meta, schema=SCHEMA, autoload_with=conn)
  person_role_table = Table("PERSON_ROLE", meta, schema=SCHEMA, autoload_with=conn)

  ethnicities_table = Table("ETHNICITIES", meta, schema=SCHEMA, autoload_with=conn)
  sexualities_table = Table("SEXUALITIES", meta, schema=SCHEMA, autoload_with=conn)
  genders_table = Table("")


def get_images(conn: Connection, movie_id:int):
  """Get images associated with movie."""
  meta = MetaData()




def _get_movie_properties(conn: Connection, PROPERTY:str, movie_id: str=None) -> pd.DataFrame:
  """ Get given properties form a movie"""
  prop_table = f"{PROPERTY}S"
  prop_movie_table = f"MOVIE_{PROPERTY}"

  prop_table = Table(prop_table, MetaData(), schema=SCHEMA, autoload_with=conn)

  if movie_id is None:
    query = prop_table.select()
  else:
    prop_movie_table = Table(prop_movie_table, MetaData(), schema=SCHEMA, autoload_with=conn)

    query = select(
      *prop_table.c
      # prop_table.c.LABEL,
      # prop_table.c.DESCRIP,
      # prop_table.c.ID,
    ).select_from(prop_movie_table).join(
      prop_table, prop_table.c.ID == prop_movie_table.c[PROPERTY+"_ID"]
    ).where(
      prop_movie_table.c.MOVIE_ID == movie_id
    )

  columns = conn.execute(query).keys()
  results = pd.DataFrame([
      _._mapping
      for _ in conn.execute(query).fetchall()
    ], columns=columns
  )
  return results

def get_genres(conn: Connection, movie_id: int=None) -> List:
  """Get genres (potential to specify movie)"""
  return _get_movie_properties(conn, "GENRE", movie_id)

def get_representations(conn: Connection, movie_id: int=None) -> Dict:
  """Get representations (potential to specify movie)"""
  return _get_movie_properties(conn, "REPRESENTATION", movie_id)

def get_tropes(conn: Connection, movie_id: int=None) -> List:
  """Get tropes (potential to specify movie)"""
  return _get_movie_properties(conn, "TROPE_TRIGGER", movie_id)

def get_characters(conn: Connection, movie_id: int=None) -> pd.DataFrame:
  """Get characters (potential to specify movie)"""
  character_table = Table("CHARACTERS", MetaData(), schema=SCHEMA, autoload_with=conn)

  query = character_table.select()
  if movie_id is not None:
    query = query.where(character_table.c.MOVIE_ID == movie_id)

  columns = conn.execute(query).keys()
  results = pd.DataFrame([
      _._mapping
      for _ in conn.execute(query).fetchall()
    ], columns=columns
  )
  return results


#TODO:  I don't know if I'll use these
def get_ratings(conn: Connection, movie_id: int=None) -> List[Dict]:
  # Use this on ui to get ratings average, how many votes
  pass

def get_quotes(conn: Connection, movie_id: int=None) -> List[Dict]:
  # Use this to get quotes for specific movie
  pass

def get_actor(conn: Connection, id: int) -> Dict:
  pass

def get_character(conn: Connection, id: int) -> Dict:
  pass
