""" Functions to save data to SQL Server."""
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

#################################################################
# Commands to save new object entries in DB
#################################################################

def save_movie(conn: Connection, movie: Dict) -> None:
  """Save movie."""
  meta = MetaData()
  pass


def save_actor(conn: Connection, actor: Dict) -> None:
  pass

def save_character(conn: Connection, character: Dict) -> None:
  pass

def save_resource(conn: Connection, resource: Dict) -> None:
  pass


def update_movie(conn: Connection, movie_id: int, properties: Dict) -> None:
  pass
def update_character(conn: Connection, character_id: int, properties: Dict) -> None:
  pass

def update_actor(conn: Connection, actor_id: int, properties: Dict) -> None:
  pass

def add_movie_images(conn: Connection, movie_id: int, images: List[str]) -> None:
  pass

def add_movie_quote(conn: Connection, movie_id: int, quote: str) -> None:
  pass

def add_movie_quality(conn: Connection, movie_id:int, quality_id: int) -> None:
  pass

def add_character_relationship(conn: Connection, character1_id:int, character2_id:int, relationship_id: int, explicit: bool=None) -> None:
  pass

###################################################################
# User Interaction Commands
###################################################################
def rate_movie(conn: Connection, movie_id: int, rating: int) -> None:
  """ Rate movie /5"""
  pass

def rate_source(conn: Connection, movie_id: int, source_id: int, rating: int) -> None:
  """Rate source for given movie."""

def add_movie_source(conn: Connection, movie_id: int, source: Dict) -> None:
  """ Add source to movie. If source doesn't pre-exist add."""
  pass



############################################################
# Commands to extend DB base types
############################################################

def add_genre(conn: Connection, label:str, descrip: str=None) -> None:
  """Add genre to database."""
  pass

def add_representation(conn: Connection, label:str, descrip: str=None) -> None:
  """Add representation to database."""
  pass

def add_relationshhip(conn: Connection, label:str, descrip: str=None) -> None:
  """Add relationship to database."""
  pass

def add_trope(conn: Connection, label:str, descrip: str=None, movie_id:int=None) -> None:
  """Add trope to database."""
  pass

def add_intensity(conn: Connection, label: str, descrip: str=None) -> None:
  pass

def add_quality(conn: Connection, label: str, descrip: str=None) -> None:
  pass


