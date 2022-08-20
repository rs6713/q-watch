""" Functions to retrieve data from SQL Server."""
import logging
from typing import Dict, List

import numpy as np
import pandas as pd
from sqlalchemy import (
    and_,
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
from sqlalchemy.orm import aliased
import sqlalchemy
from sqlalchemy.sql.expression import Alias, cast

from qwatch.utils import describe_obj

SCHEMA = "dbo"

logger = logging.getLogger(__file__)


def get_movies_ids(conn: Connection, with_year=False) -> List[Dict]:
    """ Retrieve Movie title, id list"""

    movie_table = Table("MOVIES", MetaData(),
                        schema=SCHEMA, autoload_with=conn)
    query = select(
        movie_table.c.ID,
        movie_table.c.TITLE,
        movie_table.c.YEAR,
    )

    results = {
        row._mapping["ID"]: (
            (row._mapping["TITLE"], row._mapping["YEAR"])
            if with_year else row._mapping["TITLE"])
        for row in conn.execute(query).fetchall()
    }
    return results


def get_label(conn: Connection, table_name: str, idd: str) -> int:
    """ Retrieve `LABEL` for `ID` in table"""
    table = Table(table_name, MetaData(), schema=SCHEMA, autoload_with=conn)

    query = select(
        table.c.LABEL
    ).where(
        table.c.ID == idd
    )

    return conn.execute(query).fetchall()[0]._mapping["LABEL"]


def get_id(conn: Connection, table_name: str, label: str) -> int:
    """ Retrieve `ID` for element `LABEL` in table"""
    table = Table(table_name, MetaData(), schema=SCHEMA, autoload_with=conn)

    query = select(
        table.c.ID
    ).where(
        table.c.LABEL == label
    )

    return conn.execute(query).fetchall()[0]._mapping["ID"]


def get_table_aggregate(conn: Connection, table_name: str, groups: List[str], aggs: List[str], criteria: Dict = None) -> Alias:
    """ Get string aggregate of table, using supplied groups, criteria, and aggs.
    groups - columns to group by 
    aggs - columns to string aggregate
    criteria - entries to consider
    """
    meta = MetaData()
    table = Table(table_name, meta, schema=SCHEMA, autoload_with=conn)

    query = select(
        *[table.c[g] for g in groups],
        *[func.string_agg(
            cast(table.c[agg], sqlalchemy.String),
            sqlalchemy.literal_column("','")
        ).label(agg) for agg in aggs]
    ).select_from(table)

    if criteria is not None:
        query = query.where(
            and_(*[
                table.c[key] == val
                for key, val in criteria.items()
            ])
        )

    return query.group_by(
        *[table.c[group] for group in groups]
    ).subquery()


def get_person_if_exists(conn: Connection, **actor_props) -> Dict:
    """ Retrieve Actor Firstname, last name, id list"""

    actor_table = Table("PEOPLE", MetaData(),
                        schema=SCHEMA, autoload_with=conn)

    query = select(
        *actor_table.c,
    ).select_from(
        actor_table
    ).where(
        and_(
            *[
                actor_table.c[prop] == val
                for prop, val in actor_props.items()
            ]
        )
    )

    results = pd.DataFrame([
        row._mapping
        for row in conn.execute(query).fetchall()
    ], columns=conn.execute(query).keys())

    person = results.to_dict("records")

    if len(person):
        person = person[0]
        logger.info(
            "There is a pre-existing match for person %s %s in db, loading their info..",
            person["FIRST_NAME"], person["LAST_NAME"]
        )

        ethnicities, _ = get_entries(
            conn, "PERSON_ETHNICITY", PERSON_ID=person["ID"], IS_CHARACTER=0)
        disabilities, _ = get_entries(
            conn, "PERSON_DISABILITY", PERSON_ID=person["ID"], IS_CHARACTER=0)
        if ethnicities:
            person["ETHNICITY"] = [p["ETHNICITY_ID"]
                                   for p in ethnicities]
        if disabilities:
            person["DISABILITY"] = [p["DISABILITY_ID"]
                                    for p in disabilities]
        return {
            k: v for k, v in person.items()
            if v is not None
        }

    else:
        return {}


def get_actors(conn: Connection) -> pd.DataFrame:
    """ Retrieve Actor Firstname, last name, id list"""

    actor_table = Table("PEOPLE", MetaData(),
                        schema=SCHEMA, autoload_with=conn)
    query = select(
        *actor_table.c
    ).select_from(
        actor_table
    ).order_by(actor_table.c.FIRST_NAME.desc(), actor_table.c.LAST_NAME.desc())

    results = pd.DataFrame([
        row._mapping
        for row in conn.execute(query).fetchall()
    ], columns=conn.execute(query).keys())
    return results


def get_movie(conn: Connection, movie_id: int) -> Dict:
    """Retrieve Movie by Id. """
    # Get movie details from table with matched age/intensity
    movie, _ = get_entries(conn, "MOVIES", ID=movie_id)[0][0]

    # List of all quotes in movie
    quotes, _ = get_entries(conn, "MOVIE_QUOTE", return_properties=[
                            "ID", "QUOTE", "CHARACTER_ID", "QUOTE_ID"], MOVIE_ID=movie_id, format="dataframe")

    # List of all images in movie
    images, _ = get_entries(
        conn, "MOVIE_IMAGE", return_properties=["ID", "FILENAME", "CAPTION"], MOVIE_ID=movie_id, format="dataframe"
    )

    # All ratings made against movie
    ratings, _ = get_entries(
        conn, "RATINGS", return_properties=["DATE", "RATING"], format="dataframe", MOVIE_ID=movie_id
    )

    # Get all genre, representations, tropes matched on movie_id
    types = _get_movie_properties(
        conn, "TYPE", movie_id, addit_props=["EXPLICIT"])
    genres = _get_movie_properties(conn, "GENRE", movie_id)
    representations = _get_movie_properties(
        conn, "REPRESENTATION", movie_id, addit_props=["MAIN"])
    tropes = _get_movie_properties(conn, "TROPE_TRIGGER", movie_id)
    qualities = _get_movie_properties(conn, "QUALITY", movie_id)

    sources, _ = get_entries(
        conn, "MOVIE_SOURCE", MOVIE_ID=movie_id, return_properties=["ID", "SOURCE_ID", "COST", "MEMBERSHIP_INCLUDED", "URL"], format="dataframe"
    )
    sources.loc[:, "SOURCE_ID"] = sources.SOURCE_ID.astype(int)

    # Get Characters
    characters = get_characters(conn, movie_id)

    # Get people
    people = get_people(conn, movie_id)

    # Get Character Relationships
    character_relationships, _ = get_entries(
        conn, "CHARACTER_RELATIONSHIPS", CHARACTER_ID1=list(characters.ID.values), CHARACTER_ID2=list(characters.ID.values), format="dataframe"
    )

    # Get Character Actions
    character_actions, _ = get_entries(
        conn, "CHARACTER_ACTIONS", CHARACTER_ID=list(characters.ID.values), format="dataframe"
    )
    character_actions = character_actions.groupby(
        "CHARACTER_ID").ACTION_ID.apply(list).reset_index()

    return {
        **movie,
        "TYPES": types,
        "GENRES": genres,
        "SOURCES": sources,
        "TROPE_TRIGGERS": tropes,
        "REPRESENTATIONS": representations,
        "QUOTES": quotes,
        "RATINGS": ratings,
        "QUALITIES": qualities,
        "IMAGES": images,
        "PEOPLE": people,
        "CHARACTERS": characters,
        "RELATIONSHIPS": character_relationships,
        "CHARACTER_ACTIONS": character_actions
    }


def get_characters(conn: Connection, movie_id: int) -> pd.DataFrame:
    """ Get characters associated with movie."""
    meta = MetaData()
    character_table = Table(
        "CHARACTERS", meta, schema=SCHEMA, autoload_with=conn)
    agg_ethnicity_character = get_table_aggregate(conn, "PERSON_ETHNICITY", groups=[
        "PERSON_ID"], aggs=["ETHNICITY_ID"], criteria={"IS_CHARACTER": True})
    agg_disability_character = get_table_aggregate(conn, "PERSON_DISABILITY", groups=[
        "PERSON_ID"], aggs=["DISABILITY_ID"], criteria={"IS_CHARACTER": True})

    character_query = select(
        character_table.c.ID,
        character_table.c.ACTOR_ID,
        character_table.c.FIRST_NAME,
        character_table.c.LAST_NAME,
        character_table.c.MAIN,
        character_table.c.HAIR_COLOR,
        character_table.c.GENDER,
        character_table.c.SEXUALITY,
        character_table.c.TRANSGENDER,
        agg_disability_character.c.DISABILITY_ID.label("DISABILITY"),
        agg_ethnicity_character.c.ETHNICITY_ID.label("ETHNICITY"),
        character_table.c.CAREER,
        character_table.c.BIO,
    ).select_from(character_table).join(
        agg_disability_character, agg_disability_character.c.PERSON_ID == character_table.c.ID, isouter=True
    ).join(
        agg_ethnicity_character, agg_ethnicity_character.c.PERSON_ID == character_table.c.ID, isouter=True
    ).where(
        character_table.c.MOVIE_ID == movie_id
    )
    characters = pd.DataFrame([
        row._mapping for row in conn.execute(character_query).fetchall()
    ], columns=conn.execute(character_query).keys()).groupby("ID").first().reset_index()

    for col in ["DISABILITY", "ETHNICITY"]:
        characters.loc[:, col] = characters.loc[:, col].apply(
            lambda s: s if s is None else [int(_) for _ in s.split(",")]
        )

    return characters


def get_people(conn: Connection, movie_id: int) -> pd.DataFrame:
    """Get people associated with movie."""
    meta = MetaData()

    person_role_table = Table(
        "PERSON_ROLE", meta, schema=SCHEMA, autoload_with=conn)

    people_table = Table("PEOPLE", meta, schema=SCHEMA, autoload_with=conn)

    agg_ethnicity = get_table_aggregate(conn, "PERSON_ETHNICITY", groups=[
                                        "PERSON_ID"], aggs=["ETHNICITY_ID"], criteria={"IS_CHARACTER": False})

    agg_disability = get_table_aggregate(conn, "PERSON_DISABILITY", groups=[
        "PERSON_ID"], aggs=["DISABILITY_ID"], criteria={"IS_CHARACTER": False})

    agg_role = get_table_aggregate(
        conn, "PERSON_ROLE", groups=["PERSON_ID"], aggs=["ROLE_ID"]
    )

    person_query = select(
        people_table.c.ID,
        people_table.c.BIO,
        people_table.c.FIRST_NAME,
        people_table.c.LAST_NAME,
        people_table.c.DOB,
        people_table.c.GENDER,
        people_table.c.SEXUALITY,
        people_table.c.TRANSGENDER,
        agg_ethnicity.c.ETHNICITY_ID.label("ETHNICITY"),
        agg_disability.c.DISABILITY_ID.label("DISABILITY"),
        agg_role.c.ROLE,
    ).join(
        agg_role, agg_role.c.PERSON_ID == people_table.c.ID, isouter=True
    ).join(
        agg_disability, agg_disability.c.PERSON_ID == people_table.c.ID, isouter=True
    ).join(
        agg_ethnicity, agg_ethnicity.c.PERSON_ID == people_table.c.ID, isouter=True
    ).join(
        person_role_table, person_role_table.c.PERSON_ID == people_table.c.ID
    ).where(
        person_role_table.c.MOVIE_ID == movie_id
    )

    people = pd.DataFrame([
        row._mapping for row in conn.execute(person_query).fetchall()
    ], columns=conn.execute(person_query).keys()).groupby("ID").first().reset_index()

    for col in ["ROLE", "DISABILITY", "ETHNICITY"]:
        people.loc[:, col] = people.loc[:, col].apply(
            lambda s: s if s is None else [int(_) for _ in s.split(",")]
        )

    return people


def get_entries(conn: Connection, table_name: str, ID: int = None, return_properties: List[str] = None, **properties, format="listdict") -> List[Dict]:
    """Get entries that match ID/properties from table.

    If return_properties is specified return those properties
    """
    logger.debug(
        "Fetching entry in %s, with ID %s properties:\n%s",
        table_name, str((ID or 'None')), describe_obj(properties)
    )
    table = Table(table_name, MetaData(), schema=SCHEMA, autoload_with=conn)
    table_columns = conn.execute(table.select()).keys()
    columns = [
        k for k in table_columns
        if k != "ID"
    ]

    if not all([k.upper() in columns for k in properties]):
        logger.warning(
            "%s columns not found in table %s",
            ", ".join([k for k in properties if k not in columns]),
            table_name
        )
        return [], table_columns

    def get_conditional(col, val):
        if isinstance(val, (list, np.ndarray)):
            return col.in_(list(val))
        if isinstance(val, dict):
            if val.TYPE == "GREATER_THAN":
                return col > val.VALUE
            if val.TYPE == "LESS_THAN":
                return col < val.VALUE
            if val.TYPE == "INCLUDE":
                return col.in_(val.VALUE)
            if val.TYPE == "EXCLUDE":
                return col.not_in(val.VALUE)
            if val.TYPE == "LIKE":
                return col.like(f"%{val.VALUE}%")
        return col == val

    if ID != -1 and ID is not None and ID:
        query = select(table).where(table.c.ID == ID)
    else:
        query = select(table).filter(
            *[
                get_conditional(table.c[k], v)
                for k, v in properties.items()
            ]
        )

    if return_properties is not None:
        subset_columns = [
            c for c in return_properties if c in table_columns
        ]
    else:
        subset_columns = table_columns

    matches = pd.DataFrame([
        _._mapping for _ in conn.execute(query).fetchall()
    ], columns=table_columns
    ).loc[:, subset_columns]
    logger.debug("There are %d matches", len(matches))

    if format == "listdict":
        return matches.to_dict("records"), subset_columns
    elif format == "dataframe":
        return matches, subset_columns


def get_images(conn: Connection, movie_id: int):
    """Get images associated with movie."""
    meta = MetaData()


def _get_movie_properties(conn: Connection, PROPERTY: str, movie_id: str = None, addit_props=None) -> pd.DataFrame:
    """ Get given properties form a movie"""
    prop_table = f"{PROPERTY}S"
    prop_movie_table = f"MOVIE_{PROPERTY}"

    prop_table = Table(prop_table, MetaData(),
                       schema=SCHEMA, autoload_with=conn)

    if movie_id is None:
        query = prop_table.select()
    else:
        prop_movie_table = Table(
            prop_movie_table, MetaData(), schema=SCHEMA, autoload_with=conn)

        query = select(
            *prop_table.c,
            *([] if addit_props is None else [
                prop_movie_table.c[p]
                for p in addit_props
            ])
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

    # Adding extra properties that don't exist in prop_table
    if addit_props is not None and movie_id is None:
        results.loc[:, addit_props] = None

    return results


def get_genres(conn: Connection, movie_id: int = None) -> List:
    """Get genres (potential to specify movie)"""
    return _get_movie_properties(conn, "GENRE", movie_id)


def get_representations(conn: Connection, movie_id: int = None) -> Dict:
    """Get representations (potential to specify movie)"""
    return _get_movie_properties(conn, "REPRESENTATION", movie_id, addit_props=["MAIN"])


def get_tropes(conn: Connection, movie_id: int = None) -> List:
    """Get tropes (potential to specify movie)"""
    return _get_movie_properties(conn, "TROPE_TRIGGER", movie_id)

# def get_characters(conn: Connection, movie_id: int=None) -> pd.DataFrame:
#   """Get characters (potential to specify movie)"""
#   character_table = Table("CHARACTERS", MetaData(), schema=SCHEMA, autoload_with=conn)

#   query = character_table.select()
#   if movie_id is not None:
#     query = query.where(character_table.c.MOVIE_ID == movie_id)

#   columns = conn.execute(query).keys()
#   results = pd.DataFrame([
#       _._mapping
#       for _ in conn.execute(query).fetchall()
#     ], columns=columns
#   )
#   return results


# TODO:  I don't know if I'll use these
def get_ratings(conn: Connection, movie_id: int = None) -> List[Dict]:
    # Use this on ui to get ratings average, how many votes
    pass


def get_quotes(conn: Connection, movie_id: int = None) -> List[Dict]:
    # Use this to get quotes for specific movie
    pass


def get_actor(conn: Connection, id: int) -> Dict:
    pass


def get_character(conn: Connection, id: int) -> Dict:
    pass
