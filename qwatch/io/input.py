""" Functions to retrieve data from SQL Server."""
from collections import namedtuple
import logging
from typing import Dict, List, Union

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
    update,
    Column
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

logger = logging.getLogger(__name__)

###########################################
# Traits associated with Movies
###########################################
MovieLabels = namedtuple(
    'MovieLabels', ['name', 'label', 'addit_props'], defaults=[None])
MovieEntries = namedtuple(
    'MovieEntries', ['name', 'table', 'return_properties', 'joins'], defaults=[None, None])
TableAggregate = namedtuple(
    'TableAggregate', ['table_name', 'aggs', 'groups', 'criteria'], defaults=[None]
)
TableJoin = namedtuple(
    'TableJoin', ['table', 'return_properties',
                  'base_table_prop', 'join_table_prop', 'isouter']
)
Aggregate = namedtuple(
    'Aggregate', ['property', 'label', 'func']
)

MOVIE_TRAITS = [
    MovieEntries('QUOTES', 'MOVIE_QUOTE', [
                 'ID', 'QUOTE', 'CHARACTER_ID', 'QUOTE_ID']),
    MovieEntries('IMAGES', 'MOVIE_IMAGE', ['ID', 'FILENAME', 'CAPTION']),
    MovieEntries('RATINGS', 'RATINGS', ['DATE', 'RATING']),
    MovieLabels('TYPES', 'TYPE', ['EXPLICIT']),
    MovieLabels('GENRES', 'GENRE'),
    MovieLabels('REPRESENTATIONS', 'REPRESENTATION', ['MAIN']),
    MovieLabels('TROPE_TRIGGERS', 'TROPE_TRIGGER'),
    MovieLabels('QUALITIES', 'QUALITY'),
    MovieEntries('SOURCES', 'MOVIE_SOURCE', [
                 'ID', 'SOURCE_ID', 'COST', 'MEMBERSHIP_INCLUDED', 'URL']),
    MovieEntries(name='CHARACTERS', table='CHARACTERS',
                 joins=[
                     TableJoin(
                         TableAggregate(
                             table_name=f'PERSON_{prop}',
                             aggs=[
                                 Aggregate(f'{prop}_ID', prop, 'string')
                             ],
                             groups=['PERSON_ID'],
                             criteria={'IS_CHARACTER': True}
                         ),
                         return_properties=[prop],
                         base_table_prop='ID', join_table_prop='PERSON_ID',
                         isouter=True
                     )
                     for prop in ["DISABILITY", "ETHNICITY"]
                 ]
                 ),
    MovieEntries('PEOPLE', 'PEOPLE', joins=[
        TableJoin(
            TableAggregate(
                table_name=f'PERSON_{prop}',
                aggs=[
                    Aggregate(f'{prop}_ID', prop, 'string')
                ],
                groups=["PERSON_ID"] +
                (["MOVIE_ID"] if prop == "ROLE" else []),
                criteria=(None if prop == "ROLE" else {"IS_CHARACTER": False})
            ),
            return_properties=[prop] +
            (["MOVIE_ID"] if prop == "ROLE" else []),
            base_table_prop='ID', join_table_prop='PERSON_ID',
            isouter=(False if prop == "ROLE" else True)
        )
        for prop in ["DISABILITY", "ETHNICITY", "ROLE"]
    ])
]


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


def get_table_aggregate(conn: Connection, table_name: str, groups: List[str], aggs: List[Aggregate], criteria: Dict = None) -> Alias:
    """ Get string aggregate of table, using supplied groups, criteria, and aggs.
    groups - columns to group by
    aggs - Aggregates to persom
    criteria - entries to consider
    """
    table = Table(table_name, MetaData(), schema=SCHEMA, autoload_with=conn)

    def generate_agg(agg: Aggregate):
        if agg.func == "string":
            return func.string_agg(
                cast(table.c[agg.property], sqlalchemy.String),
                sqlalchemy.literal_column("','")
            ).label(agg.label)

    query = select(
        *[table.c[g] for g in groups],
        *[generate_agg(agg) for agg in aggs]
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


def get_conditional(col: Column, val: Union[Dict, List, int, str, float]):
    """
    Get result of conditional applied to Column col.

    Params
    ------
    col: Column
        Column to apply conditional to
    val: Union[Dict, List, int, str, float]
        int/str/float --> col value must equal the literal
        List --> col value must be in the list
        Dict --> col value must satisfy conditional determined by val.VAL and val.TYPE
            - GREATER/LESS_THAN, IN/EXCLUDE, LIKE
    """
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


def is_valid_id(ID):
    """ Positive non-null ID."""
    return ID != -1 and ID is not None and ID


def get_entries(conn: Connection, table_name: str, ID: int = None, return_properties: List[str] = None, joins: List[TableJoin] = None, return_format="listdict", **properties) -> List[Dict]:
    """Get entries that match ID/properties from table, with optional joins.

    Pararms
    -------
    conn: Connection
    table_name: str
        Name of table to get entries from.
    ID: int
        (Optional) ID associated with entries
    return_format: str
        Format to return entries in [`dataframe`, `listdict`]
    return_properties: List[str]
        (Optional) Properties to return in entries, default is all.
    joins:
        (Optional) Joins to attach to main entries table, and properties to select from those.
    properties: **kw
        Criteria to filter returned entries
    """
    if len(properties.keys()) and is_valid_id(ID):
        raise ValueError(
            'Supplied both `properties` %s and valid `ID` %d to `get_entries`',
            str(properties), ID
        )

    logger.debug(
        "Fetching entry in %s, with ID %s properties:\n%s",
        table_name, str((ID or 'None')), describe_obj(properties)
    )
    table = base_table = Table(
        table_name, MetaData(), schema=SCHEMA, autoload_with=conn)
    table_columns = conn.execute(table.select()).keys()

    join_cols = []
    for join in (joins or []):
        join_cols += join.return_properties
    logger.debug("Join columns: %s", str(join_cols))
    # If criteria properties specify columns not found in table, return empty response.
    if not all([k in [*table_columns, *join_cols] for k in properties]):
        logger.warning(
            "%s columns not found in table %s",
            ", ".join([k for k in properties if k not in table_columns]),
            table_name
        )
        return ([] if return_format == "listdict" else pd.DataFrame([], columns=table_columns)), table_columns

    #query = select(table)

    # Create table joins
    join_properties = []
    join_tables = []
    for join in (joins or []):
        if isinstance(join.table, str):
            join_table = Table(join.table, MetaData(),
                               schema=SCHEMA, autoload_with=conn)
        elif isinstance(join.table, TableAggregate):
            join_table = get_table_aggregate(
                conn,
                **join.table._asdict()
            )
        table = table.join(
            join_table,
            base_table.c[join.base_table_prop] == join_table.c[join.join_table_prop],
            isouter=join.isouter
        )
        join_properties += [join_table.c[p] for p in join.return_properties]
        join_tables += [join_table]

    # ['*']
    query = select(
        *[base_table.c[col] for col in table_columns],
        *join_properties
    )

    # If ID exists, is valid, return only entries that match that id
    if is_valid_id(ID):
        query = query.where(base_table.c.ID == ID)
    else:
        # Conditionals for properties can be against join/base tables
        conditionals = []
        for k, v in properties.items():
            logger.debug(
                "Trying to create conditional for %s -> %s", k, str(v))
            for tab in [base_table, *join_tables]:
                if k in tab.c:
                    conditionals += [get_conditional(tab.c[k], v)]
                    break
            else:
                raise ValueError(
                    'Property %s not found in base/join tables %s',
                    k, str([*table_columns, *join_cols])
                )
        query = query.filter(
            *conditionals
        )

    query = query.select_from(table)

    # If return_properties exists only, return those properties
    subset_columns = [*table_columns, *join_cols]
    if return_properties is not None:
        subset_columns = [
            c for c in return_properties if c in table_columns
        ] + join_cols

    matches = pd.DataFrame([
        _._mapping for _ in conn.execute(query).fetchall()
    ], columns=[*table_columns, *join_cols]
    ).loc[:, subset_columns]
    logger.debug("There are %d matches", len(matches))

    # Convert aggregates to preferred form
    for join in (joins or []):
        if isinstance(join.table, TableAggregate):
            for agg in join.table.aggs:
                matches.loc[:, agg.label] = matches.loc[:, agg.label].apply(
                    lambda s: s if s is None else [
                        int(_) for _ in s.split(",")]
                )

    # Results of get_entries is returned in either dataframe, or List[Dict] format
    if return_format == "listdict":
        # If only one property is returned, convert to list
        if len(subset_columns) == 1:
            return [
                m[subset_columns[0]]
                for m in matches.to_dict("records")
            ]
        return matches.to_dict("records"), subset_columns
    elif return_format == "dataframe":
        return matches, subset_columns


def _get_movie_labels(conn: Connection, LABEL: str, movie_id: str = None, addit_props=None) -> pd.DataFrame:
    """ Get given many-many binary labels for a movie"""
    label_movie_table = f"MOVIE_{LABEL}"

    label_table = Table(f"{LABEL}S", MetaData(),
                        schema=SCHEMA, autoload_with=conn)

    if movie_id is None:
        query = label_table.select()
    else:
        label_movie_table = Table(
            label_movie_table, MetaData(), schema=SCHEMA, autoload_with=conn)

        query = select(
            *label_table.c,
            *([] if addit_props is None else [
                label_movie_table.c[p]
                for p in addit_props
            ])
        ).select_from(label_movie_table).join(
            label_table, label_table.c.ID == label_movie_table.c[LABEL+"_ID"]
        ).where(
            label_movie_table.c.MOVIE_ID == movie_id
        )

    columns = conn.execute(query).keys()
    results = pd.DataFrame([
        _._mapping
        for _ in conn.execute(query).fetchall()
    ], columns=columns
    )

    # Adding extra properties that don't exist in label_table
    if addit_props is not None and movie_id is None:
        results.loc[:, addit_props] = None

    return results


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


def get_movie(conn: Connection, movie_id: int, properties: List[str] = None) -> Dict:
    """
    Retrieve Movie by Id.

    Params
    ------
    conn: Connection
    movie_id: int
    properties: List[str]
        Qualities want to return associated with movie
    """
    # Get movie details from table with matched age/intensity
    movie = get_entries(conn, "MOVIES", ID=movie_id,
                        return_properties=properties)[0][0]

    for trait in MOVIE_TRAITS:
        logger.debug("Getting trait: %s", trait.name)
        # If no properties specified (default ALL) or trait in properties
        if properties is None or trait.name in properties:
            if trait.__class__.__name__ == 'MovieLabels':
                movie[trait.name] = _get_movie_labels(
                    conn, trait.label, movie_id, addit_props=trait.addit_props
                )

            elif trait.__class__.__name__ == 'MovieEntries':
                movie[trait.name] = get_entries(
                    conn, trait.table,
                    return_properties=trait.return_properties,
                    MOVIE_ID=movie_id,
                    joins=trait.joins,
                    return_format="dataframe"
                )[0]

    # # Get people
    # if properties is None or "PEOPLE" in properties:
    #     movie["PEOPLE"] = get_people(conn, movie_id)

    # Get Character Relationships
    if properties is None or "RELATIONSHIPS" in properties:
        characters = [int(i) for i in movie["CHARACTERS"].ID.values]
        movie["RELATIONSHIPS"] = get_entries(
            conn, "CHARACTER_RELATIONSHIP", CHARACTER_ID1=characters, CHARACTER_ID2=characters, return_format="dataframe"
        )[0]

    # Get Character Actions
    if properties is None or "CHARACTER_ACTIONS" in properties:
        characters = [int(i) for i in movie["CHARACTERS"].ID.values]
        movie["CHARACTER_ACTIONS"] = get_entries(
            conn, "CHARACTER_ACTION", CHARACTER_ID=characters, return_format="dataframe"
        )[0]
        movie["CHARACTER_ACTIONS"] = movie["CHARACTER_ACTIONS"].groupby(
            "CHARACTER_ID").ACTION_ID.apply(list).reset_index()

    return movie


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

        person["ETHNICITY"], _ = get_entries(
            conn, "PERSON_ETHNICITY", PERSON_ID=person["ID"], IS_CHARACTER=0,
            return_properties=["ETHNICITY_ID"])
        person["DISABILITY"], _ = get_entries(
            conn, "PERSON_DISABILITY", PERSON_ID=person["ID"], IS_CHARACTER=0,
            return_properties=["DISABILITY_ID"])

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


def get_images(conn: Connection, movie_id: int):
    """Get images associated with movie."""
    meta = MetaData()


def get_genres(conn: Connection, movie_id: int = None) -> List:
    """Get genres (potential to specify movie)"""
    return _get_movie_labels(conn, "GENRE", movie_id)


def get_representations(conn: Connection, movie_id: int = None) -> Dict:
    """Get representations (potential to specify movie)"""
    return _get_movie_labels(conn, "REPRESENTATION", movie_id, addit_props=["MAIN"])


def get_tropes(conn: Connection, movie_id: int = None) -> List:
    """Get tropes (potential to specify movie)"""
    return _get_movie_labels(conn, "TROPE_TRIGGER", movie_id)

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
