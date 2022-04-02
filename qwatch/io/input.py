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

def get_movies(conn: Connection, filters: Dict=None) -> List[Dict]:
  """Retrieve Movies that match filters."""
  meta = MetaData()
  pass

def get_movie(conn: Connection, movie_id: int) -> Dict:
  """Retrieve Movie by Id. """
  meta = MetaData()
  pass

def _get_movie_properties(conn: Connection, PROPERTY:str, movie_id: str=None) -> pd.DataFrame:
  """ Get given properties form a movie"""
  prop_table = f"{PROPERTY}S"
  prop_movie_table = f"MOVIE_{PROPERTY}"

  prop_table = Table(prop_table, MetaData(), schema=SCHEMA, autoload_with=conn)
  prop_movie_table = Table(prop_movie_table, MetaData(), schema=SCHEMA, autoload_with=conn)

  if movie_id is None:
    query = prop_table.select()
  else:
    query = select(
      prop_table.c.LABEL,
      prop_table.c.DESCRIP,
      prop_table.c.ID,
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
