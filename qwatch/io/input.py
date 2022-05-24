""" Functions to retrieve data from SQL Server."""
from typing import Dict, List

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
from sqlalchemy.sql.expression import cast

SCHEMA = "dbo"


def get_movies_ids(conn: Connection) -> List[Dict]:
    """ Retrieve Movie title, id list"""

    movie_table = Table("MOVIES", MetaData(),
                        schema=SCHEMA, autoload_with=conn)
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


def get_label(conn: Connection, table_name: str, idd: str) -> int:
    """ Retrieve id for element in table"""
    table = Table(table_name, MetaData(), schema=SCHEMA, autoload_with=conn)

    query = select(
        table.c.LABEL
    ).where(
        table.c.ID == idd
    )

    return conn.execute(query).fetchall()[0]._mapping["LABEL"]


def get_id(conn: Connection, table_name: str, label: str) -> int:
    """ Retrieve id for element in table"""
    table = Table(table_name, MetaData(), schema=SCHEMA, autoload_with=conn)

    query = select(
        table.c.ID
    ).where(
        table.c.LABEL == label
    )

    return conn.execute(query).fetchall()[0]._mapping["ID"]


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
        return person[0]
    else:
        return {}


def get_actor_ids(conn: Connection) -> pd.DataFrame:
    """ Retrieve Actor Firstname, last name, id list"""

    actor_table = Table("PEOPLE", MetaData(),
                        schema=SCHEMA, autoload_with=conn)

    query = select(
        actor_table.c.ID,
        actor_table.c.FIRST_NAME,
        actor_table.c.LAST_NAME
    ).select_from(
        actor_table
    )

    results = pd.DataFrame([
        row._mapping
        for row in conn.execute(query).fetchall()
    ], columns=["ID", "FIRST_NAME", "LAST_NAME"])
    return results


def get_movies(conn: Connection, filters: Dict = None) -> List[Dict]:
    """Retrieve Movies that match filters."""
    meta = MetaData()
    pass


def get_movie(conn: Connection, movie_id: int) -> Dict:
    """Retrieve Movie by Id. """
    meta = MetaData()

    movie_table = Table("MOVIES", meta, schema=SCHEMA, autoload_with=conn)

    movie_quote_table = Table(
        "MOVIE_QUOTE", meta, schema=SCHEMA, autoload_with=conn)
    movie_image_table = Table(
        "MOVIE_IMAGES", meta, schema=SCHEMA, autoload_with=conn
    )

    # intensity_table = Table(
    #     "INTENSITYS", meta, schema=SCHEMA, autoload_with=conn)
    # ages_table = Table("AGES", meta, schema=SCHEMA, autoload_with=conn)
    ratings_table = Table("RATINGS", meta, schema=SCHEMA, autoload_with=conn)

    # Get movie details from table with matched age/intensity
    movie_query = select(
        movie_table.c.ID,
        # ages_table.c.LABEL.label("AGE"),
        movie_table.c.AGE,
        movie_table.c.RUNTIME,
        movie_table.c.CERTIFICATE,
        movie_table.c.LANGUAGE,
        movie_table.c.SUMMARY,
        movie_table.c.BIO,
        movie_table.c.TITLE,
        movie_table.c.YEAR,
        movie_table.c.BUDGET,
        movie_table.c.BOX_OFFICE,
        movie_table.c.INTENSITY
    ).select_from(movie_table).where(
        movie_table.c.ID == movie_id
    )
    # .join(
    #     ages_table, ages_table.c.ID == movie_table.c.AGE, isouter=True
    # ).join(
    #     intensity_table, intensity_table.c.ID == movie_table.c.INTENSITY, isouter=True
    # )
    movie = conn.execute(movie_query).first()._asdict()

    # List of all quotes in movie
    quote_query = select(
        movie_quote_table.c.ID,
        movie_quote_table.c.QUOTE,
        movie_quote_table.c.CHARACTER_ID
    ).select_from(
        movie_quote_table
    ).where(
        movie_quote_table.c.MOVIE_ID == movie_id
    )
    quotes = pd.DataFrame([
        row._mapping
        for row in conn.execute(quote_query).fetchall()
    ], columns=["ID", "QUOTE", "CHARACTER_ID"]
    )
    #quotes.CHARACTER_ID.fillna(0, inplace=True)

    # List of all images in movie
    image_query = select(
        movie_image_table.c.ID,
        movie_image_table.c.FILENAME,
        movie_image_table.c.CAPTION
    ).select_from(
        movie_image_table
    ).where(
        movie_image_table.c.MOVIE_ID == movie_id
    )
    images = pd.DataFrame([
        row._mapping
        for row in conn.execute(image_query).fetchall()
    ], columns=["ID", "FILENAME", "CAPTION"]
    )

    # All ratings made against movie
    ratings_query = select(
        ratings_table.c.DATE,
        ratings_table.c.RATING
    ).where(
        ratings_table.c.MOVIE_ID == movie_id
    )
    ratings = pd.DataFrame([
        row._mapping for row in conn.execute(ratings_query).fetchall()
    ], columns=["DATE", "RATING"])

    # Get all genre, representations, tropes matched on movie_id
    types = _get_movie_properties(conn, "TYPE", movie_id)
    genres = _get_movie_properties(conn, "GENRE", movie_id)
    representations = _get_movie_properties(
        conn, "REPRESENTATION", movie_id, addit_props=["MAIN"])
    tropes = _get_movie_properties(conn, "TROPE_TRIGGER", movie_id)
    qualities = _get_movie_properties(conn, "QUALITY", movie_id)
    sources = _get_movie_properties(
        conn, "SOURCE", movie_id, addit_props=["COST", "MEMBERSHIP_INCLUDED"]
    )

    characters_people_dict = get_people(conn, movie_id)
    # TODO: Fetch images, captchas associated with movie
    #images_dict = get_images(conn, movie_id)

    return {
        **movie,
        "TYPES": types,
        "GENRES": genres,
        "SOURCES": sources,
        "TROPES": tropes,
        "REPRESENTATIONS": representations,
        "QUOTES": quotes,
        "RATINGS": ratings,
        "QUALITIES": qualities,
        "IMAGES": images,
        **characters_people_dict,
        # **images_dict
    }


def get_people(conn: Connection, movie_id: int):
    """Get people associated with movie."""
    meta = MetaData()

    roles_table = Table("ROLES", meta, schema=SCHEMA, autoload_with=conn)
    genders_table = Table("GENDERS", meta, schema=SCHEMA, autoload_with=conn)
    person_role_table = Table(
        "PERSON_ROLE", meta, schema=SCHEMA, autoload_with=conn)
    person_ethnicity_table = Table(
        "PERSON_ETHNICITY", meta, schema=SCHEMA, autoload_with=conn)
    person_disability_table = Table(
        "PERSON_DISABILITY", meta, schema=SCHEMA, autoload_with=conn)

    disabilities_table = Table(
        "DISABILITIES", meta, schema=SCHEMA, autoload_with=conn)
    ethnicities_table = Table(
        "ETHNICITIES", meta, schema=SCHEMA, autoload_with=conn)
    sexualities_table = Table(
        "SEXUALITIES", meta, schema=SCHEMA, autoload_with=conn)
    genders_table = Table("GENDERS", meta, schema=SCHEMA, autoload_with=conn)
    transgender_table = Table(
        "TRANSGENDERS", meta, schema=SCHEMA, autoload_with=conn)
    careers_table = Table("CAREERS", meta, schema=SCHEMA, autoload_with=conn)

    people_table = Table("PEOPLE", meta, schema=SCHEMA, autoload_with=conn)
    character_table = Table(
        "CHARACTERS", meta, schema=SCHEMA, autoload_with=conn)
    character_relationship_table = Table(
        "CHARACTER_RELATIONSHIPS", meta, schema=SCHEMA, autoload_with=conn)
    character_action_table = Table(
        "CHARACTER_ACTIONS", meta, schema=SCHEMA, autoload_with=conn
    )

    def get_agg_ethnicity(is_character=False):

        eth = aliased(person_ethnicity_table)
        return select(
            person_ethnicity_table.c.PERSON_ID,
            func.string_agg(cast(person_ethnicity_table.c.ETHNICITY_ID,
                            sqlalchemy.String), sqlalchemy.literal_column("','")).label("ETHNICITY")
            # func.concat(
            #     select(
            #         cast(eth.c.ETHNICITY_ID, sqlalchemy.String)
            #     ).where(eth.c.PERSON_ID == person_ethnicity_table.c.PERSON_ID)
            # ).label("ETHNICITY")
        ).select_from(person_ethnicity_table).where(
            person_ethnicity_table.c.IS_CHARACTER == is_character
        ).group_by(
            person_ethnicity_table.c.PERSON_ID
        ).subquery()

    agg_ethnicity = get_agg_ethnicity(is_character=False)
    agg_ethnicity_character = get_agg_ethnicity(is_character=True)

    def get_agg_disability(is_character=False):
        dis = aliased(person_disability_table)
        return select(
            person_disability_table.c.PERSON_ID,
            func.string_agg(cast(person_disability_table.c.DISABILITY_ID,
                            sqlalchemy.String), sqlalchemy.literal_column("','")).label("DISABILITY")
            # func.concat(
            #     select(
            #         cast(dis.c.DISABILITY_ID, sqlalchemy.String)
            #     ).where(dis.c.PERSON_ID == person_disability_table.c.PERSON_ID)
            #     #cast(person_disability_table.c.DISABILITY_ID, sqlalchemy.String)
            # ).label("DISABILITY")
        ).select_from(person_disability_table).where(
            person_disability_table.c.IS_CHARACTER == is_character
        ).group_by(
            person_disability_table.c.PERSON_ID
        ).subquery()
    agg_disability = get_agg_disability(is_character=False)
    agg_disability_character = get_agg_disability(is_character=True)

    def get_agg_role():
        dis = aliased(person_role_table)
        return select(
            person_role_table.c.PERSON_ID,
            func.string_agg(cast(person_role_table.c.ROLE_ID,
                            sqlalchemy.String), sqlalchemy.literal_column("','")).label("ROLE")
            # func.concat(
            #     select(
            #         cast(dis.c.DISABILITY_ID, sqlalchemy.String)
            #     ).where(dis.c.PERSON_ID == person_disability_table.c.PERSON_ID)
            #     #cast(person_disability_table.c.DISABILITY_ID, sqlalchemy.String)
            # ).label("DISABILITY")
        ).select_from(person_role_table).group_by(
            person_role_table.c.PERSON_ID
        ).subquery()
    agg_role = get_agg_role()

    character_query = select(
        character_table.c.CHARACTER_ID.label("ID"),
        character_table.c.ACTOR_ID,
        character_table.c.FIRST_NAME,
        character_table.c.LAST_NAME,
        character_table.c.MAIN,
        character_table.c.HAIR_COLOR,
        character_table.c.GENDER,  # genders_table.c.LABEL.label("GENDER"),
        # sexualities_table.c.LABEL.label("SEXUALITY"),
        character_table.c.SEXUALITY,
        # transgender_table.c.LABEL.label("TRANSGENDER"),
        character_table.c.TRANSGENDER,
        agg_disability_character.c.DISABILITY,
        agg_ethnicity_character.c.ETHNICITY,
        character_table.c.CAREER,
        character_table.c.BIO,
    ).select_from(character_table).join(
        agg_disability_character, agg_disability_character.c.PERSON_ID == character_table.c.CHARACTER_ID, isouter=True
    ).join(
        agg_ethnicity_character, agg_ethnicity_character.c.PERSON_ID == character_table.c.CHARACTER_ID, isouter=True
    ).where(
        character_table.c.MOVIE_ID == movie_id
    )

    """
    .join(
        genders_table, genders_table.c.ID == character_table.c.GENDER, isouter=True
    ).join(
        sexualities_table, sexualities_table.c.ID == character_table.c.SEXUALITY, isouter=True
    ).join(
        transgender_table, transgender_table.c.ID == character_table.c.TRANSGENDER, isouter=True
    )
    .join(
        careers_table, careers_table.c.ID == character_table.c.CAREER, isouter=True
    )
    """

    person_query = select(
        people_table.c.ID,
        people_table.c.BIO,
        people_table.c.FIRST_NAME,
        people_table.c.LAST_NAME,
        people_table.c.DOB,
        # people_table.c.DESCRIP,
        people_table.c.GENDER,  # genders_table.c.LABEL.label("GENDER"),
        # sexualities_table.c.LABEL.label("SEXUALITY"),
        people_table.c.SEXUALITY,
        # transgender_table.c.LABEL.label("TRANSGENDER"),
        people_table.c.TRANSGENDER,
        agg_ethnicity.c.ETHNICITY,
        agg_disability.c.DISABILITY,
        agg_role.c.ROLE,
    ).join(
        agg_role, agg_role.c.PERSON_ID == people_table.c.ID, isouter=True
    ).join(
        agg_disability, agg_disability.c.PERSON_ID == people_table.c.ID, isouter=True
    ).join(
        agg_ethnicity, agg_ethnicity.c.PERSON_ID == people_table.c.ID, isouter=True
    )
    """
    .where(
        person_role_table.c.MOVIE_ID == movie_id
    )
    .join(
        genders_table, genders_table.c.ID == people_table.c.GENDER, isouter=True
    ).join(
        sexualities_table, sexualities_table.c.ID == people_table.c.SEXUALITY, isouter=True
    ).join(
        transgender_table, transgender_table.c.ID == people_table.c.TRANSGENDER, isouter=True
    )
    """

    characters = pd.DataFrame([
        row._mapping for row in conn.execute(character_query).fetchall()
    ], columns=conn.execute(character_query).keys())

    people = pd.DataFrame([
        row._mapping for row in conn.execute(person_query).fetchall()
    ], columns=conn.execute(person_query).keys())

    for col in ["ROLE", "DISABILITY", "ETHNICITY"]:
        people.loc[:, col] = people.loc[:, col].apply(
            lambda s: s if s is None else [int(_) for _ in s.split(",")]
        )
    for col in ["DISABILITY", "ETHNICITY"]:
        characters.loc[:, col] = characters.loc[:, col].apply(
            lambda s: s if s is None else [int(_) for _ in s.split(",")]
        )

    relationship_query = select(
        character_relationship_table.c.CHARACTER_ID1,
        character_relationship_table.c.CHARACTER_ID2,
        character_relationship_table.c.RELATIONSHIP_ID,
        character_relationship_table.c.EXPLICIT
    ).where(
        and_(
            character_relationship_table.c.CHARACTER_ID1.in_(
                characters.ID),
            character_relationship_table.c.CHARACTER_ID2.in_(
                characters.ID)
        )
    )
    relationships = pd.DataFrame([
        row._mapping for row in conn.execute(relationship_query).fetchall()
    ], columns=conn.execute(relationship_query).keys())

    actions_query = select(
        character_action_table.c.CHARACTER_ID,
        character_action_table.c.ACTION_ID
    ).where(
        character_action_table.c.CHARACTER_ID.in_(characters.ID)
    )
    character_actions = pd.DataFrame([
        row._mapping for row in conn.execute(actions_query).fetchall()
    ], columns=conn.execute(actions_query).keys())
    character_actions = character_actions.groupby(
        "CHARACTER_ID").ACTION_ID.apply(list).reset_index()

    return {
        "CHARACTERS": characters,
        "PEOPLE": people,
        "RELATIONSHIPS": relationships,
        "CHARACTER_ACTIONS": character_actions,
    }


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
