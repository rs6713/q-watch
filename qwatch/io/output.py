""" Functions to save data to SQL Server."""
import datetime
import logging
import os
import shutil
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
    update, delete, and_
)
from sqlalchemy.engine import (
    Connection,
    Row,
    url,
    Engine
)

logger = logging.getLogger(__name__)

SCHEMA = "dbo"


def delete_movie(conn: Connection, movie_id: int) -> None:
    """Delete Movie."""
    logger.info("Deleting movie %d from db", movie_id)
    remove_entry(conn, "MOVIES", ID=movie_id)

    for props in ["GENRE", "REPRESENTATION", "TROPE_TRIGGER", "TYPE", "IMAGE", "QUOTE", "SOURCE"]:
        remove_entry(conn, f"MOVIE_{props}", MOVIE_ID=movie_id)

    ##################################################
    # Remove People, Characters, Actions
    ##################################################
    remove_entry(conn, "PERSON_ROLE", MOVIE_ID=movie_id)
    characters = remove_entry(
        conn, "CHARACTERS", MOVIE_ID=movie_id, return_prop="CHARACTER_ID")

    if len(characters):
        remove_entry(conn, "CHARACTER_RELATIONSHIPS", CHARACTER_ID1=characters)
        remove_entry(conn, "CHARACTER_RELATIONSHIPS", CHARACTER_ID2=characters)
        remove_entry(conn, "CHARACTER_ACTIONS", CHARACTER_ID=characters)


def save_movie(conn: Connection, movie: Dict) -> None:
    """Save/Update movie."""
    if movie.get("ID", None) is not None:
        # We are not editing movie
        delete_movie(conn, movie["ID"])

    movie_id = add_entry(conn, "MOVIES", **movie)

    #############################################
    # Images
    ############################################
    img_dir = os.path.join(
        Path(__name__).parent.parent.parent,
        "website", "src", "static", "movie-pictures")
    img_dst = MOVIE["TITLE"].lower().replace(
        " ", "-") + "_" + str(MOVIE["YEAR"])
    existing_img_n = len([
        f for f in listdir(img_dir)
        if f.contains(img_dst)
    ])
    for image in movie["IMAGES"]:
        try:
            if image["ID"] is None or not image["ID"]:
                ext = image["FILENAME"].split(".")[1]
                dst = os.path.join(
                    img_dir,
                    img_dst + f"-{existing_img_n:03d}.{ext}"
                )
                shutil.copyfile(image["FILENAME"], dst)
                image["FILENAME"] = img_dst + f"-{existing_img_n:03d}.{ext}"
                existing_img_n += 1
        except Exception as e:
            logger.warning(
                "Failed to copy over image: %s",
                image["FILENAME"]
            )
            continue
        # Hard reset image ID as won't exist anymore
        image["ID"] = None
        add_entry(conn, "MOVIE_IMAGES", MOVIE_ID=movie_id, **image)

    ################################################
    # Sources
    ###############################################
    for source in movie["SOURCES"]:
        add_entry(conn, "MOVIE_SOURCES", MOVIE_ID=movie_id, **source)

    ##############################################
    # Quotes
    ##############################################
    for quote in movie["QUOTES"]:
        add_entry(conn, "MOVIE_QUOTES", MOVIE_ID=movie_id, **quote)

    ################################################
    # Genres, Tropes, Representations, Types
    ################################################
    for props in ["GENRE", "REPRESENTATION", "TROPE_TRIGGER", "TYPE"]:
        for selected_option in movie[props + "S"]:
            add_entry(conn, f"MOVIE_{props}",
                      MOVIE_ID=movie_id, **selected_option)

    #############################################
    # People, Characters, Actions, Relationships
    #############################################
    # TODO More complex update of PERSON, properties, don't delete, recreate
    person_id_mappings = {}
    for person in movie["PEOPLE"]:
        orig_person_id = person["ID"]
        person_id = add_entry(conn, "PEOPLE", **person)
        person_id_mappings[orig_person_id] = person_id
        for role_id in person["ROLES"]:
            add_entry(
                conn, "PERSON_ROLE",
                PERSON_ID=person_id, MOVIE_ID=movie_id, ROLE_ID=role_id
            )

    for character in movie["CHARACTERS"]:
        character["ACTOR_ID"] = person_id_mappings[character["ACTOR_ID"]]
        character["MOVIE_ID"] = movie_id
        add_entry(
            conn, "CHARACTERS", **character
        )
    for action in movie["CHARACTER_ACTIONS"]:
        add_entry(conn, "CHARACTER_ACTIONS", **action)
    for relationship in movie["RELATIONSHIPS"]:
        add_entry(conn, "CHARACTER_RELATIONSHIPS", **relationship)

# TODO Handle list prop, not single val , isin


def remove_entry(conn: Connection, table_name: str, return_prop=None, **properties) -> None:
    """Delete entry from table."""
    logger.info(
        "Deleting entry from %s, with props: %s",
        table_name, str(properties)
    )

    table = Table(
        table_name, MetaData(), schema=SCHEMA, autoload_with=conn
    )
    if not properties:
        logger.error(
            "Cannot delete entries from table %s with no matching properties given", table_name)
        return

    results = None

    if return_prop is not None:
        query = select(table.c[return_prop]).where(
            and_(
                *[
                    table.c[key] == val if not isinstance(
                        val, list) else table.c[key].isin(val)
                    for key, val in properties.items()
                ]
            )
        )
        results = pd.DataFrame([
            _._mapping for _ in conn.execute(query).fetchall()
        ], columns=conn.execute(query).keys())[return_prop].values

    delete(table).where(
        and_(
            *[
                table.c[key] == val if not isinstance(
                    val, list) else table.c[key].isin(val)
                for key, val in properties.items()
            ]
        )
    )
    logger.info("Deleted entries matching %s from table %s.",
                str(properties), table_name)

    return results


# TODO Handle case where characters are deleted.
# TODO Handle case where keys are not ID
# TODO Handle case where id is fake generated
def add_entry(conn: Connection, table_name: str, ID: int = None, **properties) -> None:
    """Add/Update entry in specified table. Return generated/existing id."""
    logger.info(
        "Adding entry to %s, with props: %s",
        table_name, str(properties)
    )
    table = Table(
        table_name, MetaData(), schema=SCHEMA, autoload_with=conn
    )

    columns = conn.execute(table.select()).keys()

    if not all([k.upper() in columns for k in properties]):
        logger.debug(
            "%s columns not found in table %s",
            ", ".join([k for k in properties if k not in columns]),
            table_name
        )

    properties = {k: v for k, v in properties.items() if k in columns}

    # ID should not be equal to 0
    if ID is not None and ID:
        logger.info("Inserting entry to %s", table_name)
        conn.execute(update(table).where(table.c.ID == id).values(properties))
        return ID
    else:
        logger.info("Updating entry %d in %s", ID, table_name)
        properties = {c: properties.get(c, None) for c in columns}
        result = conn.execute(
            table.insert(), properties
        )
        return result.inserted_primary_key

###################################################################
# User Interaction Commands
###################################################################


def rate_movie(conn: Connection, movie_id: int, rating: int, id: int = None) -> None:
    """ Rate movie /5. Update user rating, or new one"""

    vote_time = datetime.datetime.now()
    add_entry(conn, "RATINGS", id=id, movie_id=movie_id,
              rating=rating, date=vote_time)


def add_source(conn: Connection, movie_id: int = None, id: int = None, source_id: int = None, vote: int = None, **kw) -> None:
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
            vote=1 if kw else vote  # vote is 1, if source has just been added
        )


def remove_source(conn: Connection, source_id: int = None, movie_id: int = None):
    # No option to remove a specific vote, only change (see func above)
    # Remove all (source, movie) votes from MOVIE_SOURCE
    # If movie_id is None, remove all instance of (source, movie) and source
    pass


def remove_genre(conn: Connection, genre_id: int = None, movie_id: int = None):
    # savme as above
    pass


def remove_trope_trigger(conn: Connection, trope_trigger_id: int = None, movie_id: int = None):
    # savme as above
    pass


def remove_representation(conn: Connection, representation_id: int = None, movie_id: int = None):
    # savme as above
    pass


############################################################
# Commands to extend DB base types
############################################################


def save_actor(conn: Connection, actor: Dict, id: int = None,) -> None:
    add_entry(conn, "ACTORS", id=id, **actor)


def save_character(conn: Connection, character: Dict, id: int = None) -> None:
    add_entry(conn, "CHARACTERS", id=id, **character)


def add_movie_quote(conn: Connection, id: int = None, **kw) -> None:
    """Add quote to database. If ID supplied, updates entry, else adds"""
    if kw:
        id = add_entry(conn, "MOVIE_QUOTE", id=id, **kw)


def add_genre(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """Add genre to database."""
    if kw:
        id = add_entry(conn, "GENRES", id=id, **kw)
    if movie_id is not None and id is not None:
        add_entry(conn, "MOVIE_GENRE", movie_id=movie_id, genre_id=id)


def add_representation(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """Add representation to database, optionally apply to movie"""
    if kw:
        id = add_entry(conn, "REPRESENTATIONS", id=id, **kw)
    if movie_id is not None and id is not None:
        add_entry(conn, "MOVIE_REPRESENTATION",
                  movie_id=movie_id, representation_id=id)


def add_relationship(conn: Connection, character_id1: int = None, character_id2: int = None, explicit: int = None, id: int = None, **kw) -> None:
    """Add relationship to database."""
    if kw:
        id = add_entry(conn, "RELATIONSHIPS", id=id, **kw)

    if character_id1 is not None and character_id2 is not None and id is not None:
        add_entry(conn, "CHARACTER_RELATIONSHIP", character_id1=character_id1,
                  character_id2=character_id2, relationship_id=id, explict=explicit)


def add_trope(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """ Add/Update new Trope Type, then optionally add relation to movie."""
    if kw:
        id = add_entry(conn, "TROPE_TRIGGERS", id=id, **kw)

    if movie_id is not None and id is not None:
        add_entry(conn, "MOVIE_TROPE_TRIGGER",
                  movie_id=movie_id, trope_trigger_id=id)


def add_intensity(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """ Add/Update new Intensity Type, then optionally add relation to movie."""
    if kw:
        add_entry(conn, "INTENSITIES", id=id, **kw)
    if movie_id is not None and id is not None:
        add_entry(conn, "MOVIE_INTENSITY", movie_id=movie_id, intensity_id=id)


def add_quality(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """ Add/Update new Quality Type, then optionally add relation to movie."""
    if kw:
        id = add_entry(conn, "QUALITIES", id=id, **kw)
    if movie_id is not None and id is not None:
        add_entry(conn, "MOVIE_QUALITY", movie_id=movie_id, quality_id=id)
