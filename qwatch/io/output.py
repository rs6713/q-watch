""" Functions to save data to SQL Server."""
import datetime
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

def add_entry(conn: Connection, table_name:str, id=None, **properties) -> None:
  """Add/Update entry in specified table. Return generated id."""
  table = Table(
    table_name, MetaData(), schema=SCHEMA, autoload_with=conn
  )

  columns = conn.execute(table.select()).keys()

  if not all([k.upper() in columns for k in properties]):
    raise ValueError(
      "%s columns not found in table %s",
      ", ".join([k for k in properties if k not in columns]),
      table_name
    )

  properties = {k.upper(): v for k, v in properties.items()}

  if id is not None:
    conn.execute(update(table).where(table.c.ID==id).values(properties))
    return id
  else:
    properties = {c: properties.get(c, None) for c in columns}
    result = conn.execute(
      table.insert(), properties
    )
    return result.inserted_primary_key

###################################################################
# User Interaction Commands
###################################################################
def rate_movie(conn: Connection, movie_id: int, rating: int, id:int=None) -> None:
  """ Rate movie /5. Update user rating, or new one"""

  vote_time = datetime.datetime.now()
  add_entry(conn, "RATINGS", id=id, movie_id=movie_id, rating=rating, date=vote_time)

def add_source(conn: Connection, movie_id: int=None, id: int=None, source_id:int=None, vote:int=None, **kw) -> None:
  """ Add source to movie. Or change/add new vote . If source doesn't pre-exist add, otherwise update is properties supplied."""
  # If there are new source properties need to insert/update them
  if kw:
    source_id = add_entry(conn, "SOURCES", id=id, **kw)

  if movie_id is not None and id is not None and source_id is not None:
    add_entry(
      conn, "MOVIE_SOURCE",
      movie_id=movie_id,
      id=id,
      source_id=source_id,
      date=datetime.datetime.now(),
      vote=1 if kw else vote # vote is 1, if source has just been added
    )

def remove_source(conn: Connection, source_id:int=None, movie_id:int=None):
  # No option to remove a specific vote, only change (see func above)
  # Remove all (source, movie) votes from MOVIE_SOURCE
  # If movie_id is None, remove all instance of (source, movie) and source
  pass

def remove_genre(conn: Connection, genre_id: int=None, movie_id:int=None):
  # savme as above
  pass

def remove_trope_trigger(conn: Connection, trope_trigger_id: int=None, movie_id:int=None):
  # savme as above
  pass

def remove_representation(conn: Connection, representation_id: int=None, movie_id:int=None):
  # savme as above
  pass


############################################################
# Commands to extend DB base types
############################################################

def save_movie(conn: Connection, movie: Dict, id:int = None) -> None:
  """Save/Update movie."""
  add_entry(conn, "MOVIES", id=id, **movie)

def save_actor(conn: Connection, actor: Dict, id:int=None,) -> None:
  add_entry(conn, "ACTORS", id=id, **actor)

def save_character(conn: Connection, character: Dict, id:int=None) -> None:
  add_entry(conn, "CHARACTERS", id=id, **character)


def add_movie_quote(conn: Connection, id:int=None, **kw) -> None:
  """Add quote to database. If ID supplied, updates entry, else adds"""
  if kw:
    id = add_entry(conn, "MOVIE_QUOTE", id=id, **kw)


def add_genre(conn: Connection, id:int=None, movie_id:int=None **KW) -> None:
  """Add genre to database."""
  if kw:
    id = add_entry(conn, "GENRES", id=id, **kw)
  if movie_id is not None and id is not None:
    add_entry(conn, "MOVIE_GENRE", movie_id=movie_id, genre_id=id)

def add_representation(conn: Connection, id:int=None, movie_id:int=None, **kw) -> None:
  """Add representation to database, optionally apply to movie"""
  if kw:
    id = add_entry(conn, "REPRESENTATIONS", id=id, **kw)
  if movie_id is not None and id is not None:
    add_entry(conn, "MOVIE_REPRESENTATION", movie_id=movie_id, representation_id=id)

def add_relationship(conn: Connection, character_id1:int=None, character_id2:int=None, explicit:int=None, id:int=None, **kw) -> None:
  """Add relationship to database."""
  if kw:
    id = add_entry(conn, "RELATIONSHIPS", id=id, **kw)

  if character_id1 is not None and character_id2 is not None and id is not None:
    add_entry(conn, "CHARACTER_RELATIONSHIP", character_id1=character_id1, character_id2=character_id2, relationship_id=id, explict=explicit)

def add_trope(conn: Connection, id:int=None, movie_id:int=None, **kw) -> None:
  """ Add/Update new Trope Type, then optionally add relation to movie."""
  if kw:
    id = add_entry(conn, "TROPE_TRIGGERS", id=id, **kw)

  if movie_id is not None and id is not None:
    add_entry(conn, "MOVIE_TROPE_TRIGGER", movie_id=movie_id, trope_trigger_id=id)

def add_intensity(conn: Connection, id:int=None, movie_id:int=None, **kw) -> None:
  """ Add/Update new Intensity Type, then optionally add relation to movie."""
  if kw:
    add_entry(conn, "INTENSITIES", id=id, **kw)
  if movie_id is not None and id is not None:
    add_entry(conn, "MOVIE_INTENSITY", movie_id=movie_id, intensity_id=id)

def add_quality(conn: Connection, id:int=None, movie_id:int=None, **kw) -> None:
  """ Add/Update new Quality Type, then optionally add relation to movie."""
  if kw:
    id = add_entry(conn, "QUALITIES", id=id, **kw)
  if movie_id is not None and id is not None:
    add_entry(conn, "MOVIE_QUALITY", movie_id=movie_id, quality_id=id)
