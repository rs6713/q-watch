""" Functions to save data to SQL Server."""
import datetime
import logging
import numbers
import os
from pathlib import Path
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

from qwatch.io.input import get_entries
from qwatch.utils import describe_obj

logger = logging.getLogger(__name__)

SCHEMA = "dbo"


def delete_movie(conn: Connection, movie_id: int) -> None:
    """Delete Movie."""
    if movie_id == -1:
        return

    logger.info("Deleting movie %d from db", movie_id)

    ##############################
    # Remove movie entry in MOVIES
    ##############################
    remove_entry(conn, "MOVIES", ID=movie_id)

    ###################################
    # Remove genre, representation, tropes, types, images, quotes, sources
    ###################################
    for props in ["GENRE", "REPRESENTATION", "TROPE_TRIGGER", "TYPE", "IMAGE", "QUOTE", "SOURCE"]:
        removed_entries = remove_entry(
            conn, f"MOVIE_{props}", return_prop="ID", MOVIE_ID=movie_id)
        # Remove votes associated with MOVIE_SOURCE
        if props == "SOURCE":
            remove_entry(conn, "MOVIE_SOURCE_VOTE",
                         MOVIE_SOURCE=removed_entries)

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


def save_movie_legacy(conn: Connection, movie: Dict) -> int:
    """Save/Update movie. Returns int of created movie id"""
    logger.info("Saving movie: %s", movie["TITLE"])
    if movie.get("ID", -1) != -1:
        # We are not editing movie
        delete_movie(conn, movie["ID"])
    else:
        logger.info(
            f"No pre-existing movie entry to remove for {movie['TITLE']}")

    ############################################
    # Clean movie information
    ############################################
    movie = clean_movie(movie)

    #############################################
    # Insert movie into DB
    #############################################
    movie_id = add_update_entry(conn, "MOVIES", **movie)

    #############################################
    # Images
    ############################################
    img_dir = os.path.join(
        Path(__name__).parent.parent.parent,
        "website", "src", "static", "movie-pictures")
    img_dst = movie["TITLE"].lower().replace(
        " ", "-") + "_" + str(movie["YEAR"])

    existing_img_n = len([
        f for f in os.listdir(img_dir)
        if img_dst in f
    ])
    logger.info("Moving %s to %s.", img_dst, img_dir)

    for image in (movie["IMAGES"] or []):
        try:
            if image["ID"] is None or not image["ID"] or image["ID"] == -1:
                ext = image["FILENAME"].split(".")[1]
                dst = os.path.join(
                    img_dir,
                    img_dst + f"-{existing_img_n:03d}.{ext}"
                )
                shutil.copyfile(image["FILENAME"], dst)
                image["FILENAME"] = img_dst + f"-{existing_img_n:03d}.{ext}"
                existing_img_n += 1
                logger.info("Copying image to %s", image["FILENAME"])
        except Exception as e:
            logger.warning(
                "Failed to copy over image: %s",
                image["FILENAME"]
            )
            continue
        # Hard reset image ID as won't exist anymore
        image["ID"] = None
        logger.info("Adding image for movie %d", movie_id)
        add_update_entry(conn, "MOVIE_IMAGE", MOVIE_ID=movie_id, **image)

    ################################################
    # Sources
    ###############################################
    logger.info("Adding %d sources", len((movie["SOURCES"] or [])))
    for source in (movie["SOURCES"] or []):
        add_update_entry(conn, "MOVIE_SOURCE", MOVIE_ID=movie_id, **source)

    ##############################################
    # Quotes
    ##############################################
    logger.info("Adding %d quotes", len((movie["QUOTES"] or [])))
    for quote in (movie["QUOTES"] or []):
        add_update_entry(conn, "MOVIE_QUOTE", MOVIE_ID=movie_id, **quote)

    ################################################
    # Genres, Tropes, Representations, Types
    ################################################
    for props in ["GENRE", "REPRESENTATION", "TROPE_TRIGGER", "TYPE"]:
        logger.info("Saving  %d %sS", len((movie[props + "S"] or [])), props)
        for selected_option in (movie[props + "S"] or []):
            add_update_entry(conn, f"MOVIE_{props}",
                             MOVIE_ID=movie_id, **selected_option)

    #############################################
    # People, Characters, Actions, Relationships
    #############################################
    # TODO More complex update of PERSON, properties, don't delete, recreate
    person_id_mappings = {}
    logger.info("Adding %d people", len((movie["PEOPLE"] or [])))
    for person in (movie["PEOPLE"] or []):
        orig_person_id = person["ID"]
        person_id = add_update_entry(conn, "PEOPLE", **person)
        person_id_mappings[orig_person_id] = person_id
        for role_id in person["ROLES"]:
            add_update_entry(
                conn, "PERSON_ROLE",
                PERSON_ID=person_id, MOVIE_ID=movie_id, ROLE_ID=role_id
            )

    logger.info("Adding %d characters", len((movie["CHARACTERS"] or [])))
    for character in (movie["CHARACTERS"] or []):
        character["ACTOR_ID"] = person_id_mappings[character["ACTOR_ID"]]
        character["MOVIE_ID"] = movie_id
        add_update_entry(
            conn, "CHARACTERS", **character
        )

    logger.info("Adding %d character actions", len(
        (movie["CHARACTER_ACTIONS"] or [])))
    for action in (movie["CHARACTER_ACTIONS"] or []):
        add_update_entry(conn, "CHARACTER_ACTIONS", **action)

    logger.info("Adding %d character relationship",
                len((movie["RELATIONSHIPS"] or [])))
    for relationship in (movie["RELATIONSHIPS"] or []):
        add_update_entry(conn, "CHARACTER_RELATIONSHIPS", **relationship)

    return movie_id


def clean_movie(movie: Dict) -> Dict:
    """ Clean Movie Information, suitable for storage."""
    logger.info(
        "Performing movie cleaning --> Converting entries to correct type")
    for k in movie:
        try:
            if movie[k] == -1:
                movie[k] = None
        # Handle exception in case is dataframe
        except Exception as e:
            continue
        if k in ["YEAR", "RUNTIME", "BOX_OFFICE"]:
            movie[k] = int(''.join([c for c in movie[k] if c.isnumeric()]))
    # for k in ["IMAGES", "SOURCES", "CHARACTERS", "CHARACTER_ACTIONS", "GENRE", "REPRESENTATION", "TROPE_TRIGGER", "TYPE", "PEOPLE", "RELATIONSHIPS"]:

    #######################
    # Insert Images into DB
    #######################
    if movie["IMAGES"] is not None and len(movie["IMAGES"]):
        img_dir = os.path.join(
            Path(__name__).parent.parent.parent,
            "website", "src", "static", "movie-pictures")
        img_dst = movie["TITLE"].lower().replace(
            " ", "-") + "_" + str(movie["YEAR"])

        existing_imgs = [
            int(f.split("-")[-1].split(".")[0])
            for f in os.listdir(img_dir)
            if img_dst in f
        ]
        if existing_imgs:
            existing_img_n = max(existing_imgs) + 1
        else:
            existing_img_n = 0

        for image in movie["IMAGES"]:
            try:
                if image["ID"] is None or not image["ID"] or image["ID"] == -1:
                    ext = image["FILENAME"].split(".")[1]
                    dst = os.path.join(
                        img_dir,
                        img_dst + f"-{existing_img_n:03d}.{ext}"
                    )
                    shutil.copyfile(image["FILENAME"], dst)
                    image["FILENAME"] = img_dst + \
                        f"-{existing_img_n:03d}.{ext}"
                    existing_img_n += 1
                    logger.info("Copying image to %s", image["FILENAME"])
                else:
                    logger.info("Keeping image")
            except Exception as e:
                logger.warning(
                    "Failed to copy over image: %s",
                    image["FILENAME"]
                )
                continue

    return movie


def update_agg_entry_list(conn: Connection, table_name: str, entry_list: List[int], **match_criteria) -> None:
    """
    Update entries that are aggregates.
    """
    logger.info("Agg Entry Saving/Updating  %d entries in %s",
                len((entry_list or [])), table_name)
    agg_prop = table_name.split("_")[-1]

    existing_entries, _ = get_entries(conn, table_name, **match_criteria)
    new_ids = []

    # If there are new entries to add.
    if entry_list is not None and len(entry_list):
        # Remove deleted entries
        removed_entries = [
            entry["ID"] for entry in existing_entries
            if entry[agg_prop+"_ID"] not in entry_list
        ]
        logger.info("Deleting %d entries in %s",
                    len(removed_entries), table_name)
        for entry_id in removed_entries:
            remove_entry(conn, table_name, ID=entry_id)

        # Update / Add New Entries
        logger.info("Adding %d entries", len(entry_list or []))
        for entry in entry_list:
            # Allows for overlap properties
            new_entry = {agg_prop+"_ID": entry, **match_criteria}
            new_ids += [
                add_update_entry(conn, table_name, **new_entry)
            ]

    else:
        # Remove all existing entries
        remove_entry(conn, table_name, **match_criteria)

    return new_ids


def update_entry_list(conn: Connection, table_name: str, entry_list: List[Dict], **match_criteria) -> None:
    """
    For list of entries for table property associated with movie, update records in DB.

    Check for entries that have been deleted, and remove.
    Update/add new entries.
    """
    logger.info("Saving/Updating  %d entries in %s",
                len((entry_list or [])), table_name)

    existing_entries, _ = get_entries(conn, table_name, **match_criteria)
    new_entries = [
        e["ID"] for e in entry_list
        if "ID" in e
    ]

    new_ids = []

    # If there are new entries to add.
    if entry_list is not None and len(entry_list):
        # Remove deleted entries
        removed_entries = [
            entry["ID"] for entry in existing_entries
            if entry["ID"] not in new_entries
        ]
        logger.info("Deleting %d entries in %s",
                    len(removed_entries), table_name)
        for entry_id in removed_entries:
            remove_entry(conn, table_name, ID=entry_id)

        # Update / Add New Entries
        logger.info("Adding %d entries", len(entry_list or []))
        for entry in entry_list:
            # Allows for overlap properties
            new_entry = {**entry, **match_criteria}
            new_ids += [
                add_update_entry(conn, table_name, **new_entry)
            ]
    else:
        # Remove all existing entries
        remove_entry(conn, table_name, **match_criteria)

    return new_ids

# done - Todo check for actors pre-existing/writers, to update returned info for table
# DONE- todo Correct ROLES so they have associated ID property when loaded from db, LIST DICT FORM


def save_movie(conn: Connection, movie: Dict) -> int:
    """Save/Update movie. Returns int of created movie id"""
    logger.info("Saving movie: %s, pre-existing id: %d",
                movie["TITLE"], movie["ID"])
    MOVIE_EXISTS = movie..get("ID", -1) != -1

    #################################################
    # Clean movie information - sort movie images dir
    #################################################
    movie = clean_movie(movie)

    ######################
    # Insert movie into DB
    ######################
    movie_id = add_update_entry(conn, "MOVIES", **movie)

    try:

        # Update movie props lists (many to many simple relationships)
        update_props = [
            "SOURCE",
            "TROPE_TRIGGER",
            "QUOTE",
            "GENRE",
            "REPRESENTATION",
            "TYPE",
            "IMAGE",
        ]
        for prop in update_props:
            _ = update_entry_list(
                conn, f"MOVIE_{prop}", movie[f"{prop}S"], MOVIE_ID=movie_id
            )

        ############################################
        # People, Characters, Actions, Relationships
        ############################################
        logger.info("Adding %d people", len((movie["PEOPLE"] or [])))

        existing_roles, _ = get_entries(conn, "PERSON_ROLE", MOVIE_ID=movie_id)

        person_id_mappings = {}
        # Person
        for person in (movie["PEOPLE"] or []):
            # Existing ID, not generated
            if isinstance(person["ID"], numbers.Number) and len(str(person["ID"])) < 15:
                person["ID"] = int(person["ID"])
                _ = add_update_entry(conn, "PEOPLE", **person)
                person_id_mappings[person["ID"]] = person["ID"]
            # Generated ids from uuid are 20 long.
            else:
                orig_person_id = person["ID"]
                person["ID"] = None
                person["ID"] = add_update_entry(conn, "PEOPLE", **person)
                person_id_mappings[orig_person_id] = person["ID"]

            # Add ROLES, DISABILITIES, ETHNICITIES
            for prop in ["ROLE", "DISABILITY", "ETHNICITY"]:
                if prop in person:
                    if prop == "ROLE":
                        _ = update_agg_entry_list(
                            conn, f"PERSON_{prop}", person[prop],
                            PERSON_ID=person["ID"], MOVIE_ID=movie_id
                        )
                    else:
                        _ = update_agg_entry_list(
                            conn, f"PERSON_{prop}", person[prop],
                            PERSON_ID=person["ID"], IS_CHARACTER=0
                        )
                else:
                    logger.warning(
                        "Couldn't update agg entry list %s as doesn't exist in people",
                        prop
                    )

        existing_characters = [
            c["ID"] for c in get_entries(
                conn, "CHARACTERS", MOVIE_ID=movie_id
            )[0]
        ]
        logger.info("Adding %d characters", len((movie["CHARACTERS"] or [])))
        character_id_mappings = {}
        if movie["CHARACTERS"] is not None and len(movie["CHARACTERS"]):
            for character in movie["CHARACTERS"]:
                character["ACTOR_ID"] = person_id_mappings[character["ACTOR_ID"]]
                character["MOVIE_ID"] = movie_id

                if isinstance(character["ID"], numbers.Number) and len(str(character["ID"])) < 15:
                    character_id_mappings[character["ID"]] = character["ID"]
                # Generated ids from uuid are 20 long.
                else:
                    orig_character_id = character["ID"]
                    character["ID"] = None
                    character["ID"] = add_update_entry(
                        conn, "CHARACTERS", **character)
                    character_id_mappings[orig_character_id] = character["ID"]

            _ = update_entry_list(
                conn, "CHARACTERS", movie["CHARACTERS"], MOVIE_ID=movie_id
            )
            for character in movie["CHARACTERS"]:
                # Add DISABILITIES, ETHNICITIES
                for prop in ["DISABILITY", "ETHNICITY"]:
                    if prop in character:
                        _ = update_agg_entry_list(
                            conn, f"PERSON_{prop}", character[prop],
                            PERSON_ID=character["ID"], IS_CHARACTER=1,
                        )
                    else:
                        logger.warning(
                            "Couldn't update agg entry list %s as doesn't exist in character",
                            prop
                        )

        logger.info("Adding %d character actions", len(
            (movie["CHARACTER_ACTIONS"] or [])))
        if movie["CHARACTER_ACTIONS"] is not None and len(movie["CHARACTER_ACTIONS"]):
            movie["CHARACTER_ACTIONS"] = [
                {**ca,
                    "CHARACTER_ID": character_id_mappings[ca["CHARACTER_ID"]]}
                for ca in movie["CHARACTER_ACTIONS"]
            ]
            _ = update_entry_list(
                conn, "CHARACTER_ACTIONS", movie["CHARACTER_ACTIONS"],
                CHARACTER_ID=existing_characters
            )

        logger.info("Adding %d character relationship",
                    len((movie["RELATIONSHIPS"] or [])))
        if movie["RELATIONSHIPS"] is not None and len(movie["RELATIONSHIPS"]):
            movie["RELATIONSHIPS"] = [
                {
                    **r,
                    "CHARACTER_ID1": character_id_mappings[r["CHARACTER_ID1"]],
                    "CHARACTER_ID2": character_id_mappings[r["CHARACTER_ID2"]]
                }
                for r in movie["RELATIONSHIPS"]
            ]
            _ = update_entry_list(
                conn, "RELATIONSHIPS", movie["RELATIONSHIPS"],
                CHARACTER_ID1=existing_characters
            )
    except Exception as e:
        logger.error(
            "Error while saving movie %s, %s.",
            movie_id, movie["TITLE"]
        )
        if not MOVIE_EXISTS:
            logger.error(
                "Cancelling movie creation process, and deleting all references")
            delete_movie(conn, movie_id)
        raise e

    return movie_id


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

    # Return list of return_prop, that represent items deleted
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
        ], columns=[return_prop])[return_prop].values

    # Handle case where FILENAME in dir
    if table == "MOVIE_IMAGE":
        query = select(table.FILENAME).where(
            and_(
                *[
                    table.c[key] == val if not isinstance(
                        val, list) else table.c[key].isin(val)
                    for key, val in properties.items()
                ]
            )
        )
        imgs = pd.DataFrame([
            _._mapping for _ in conn.execute(query).fetchall()
        ], columns=["FILENAME"])["FILENAME"].values

        img_dir = os.path.join(
            Path(__name__).parent.parent.parent,
            "website", "src", "static", "movie-pictures"
        )
        for img in imgs:
            logger.info("Deleting file %s", os.path.join(img_dir, img))
            os.remove(os.path.join(img_dir, img))

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


# TODO Handle case where keys are not ID

def add_update_entry(conn: Connection, table_name: str, ID: int = None, **properties) -> None:
    """Add/Update entry in specified table. Return generated/existing id."""
    logger.debug(
        "Adding entry to %s, with props:\n%s",
        table_name, describe_obj(properties)
    )
    table = Table(
        table_name, MetaData(), schema=SCHEMA, autoload_with=conn
    )

    columns = [
        k for k in conn.execute(table.select()).keys()
        if k != "ID"
    ]

    if not all([k.upper() in columns for k in properties]):
        logger.warning(
            "%s columns not found in table %s",
            ", ".join([k for k in properties if k not in columns]),
            table_name
        )

    properties = {k: v for k, v in properties.items() if k in columns}

    # ID should not be equal to 0
    if ID != -1 and ID is not None and ID:
        logger.info("Updating entry %d in %s", ID, table_name)
        conn.execute(update(table).where(table.c.ID == ID).values(properties))
        return ID
    else:
        logger.info("Inserting entry to %s", table_name)
        properties = {c: properties.get(c, None) for c in columns}
        result = conn.execute(
            table.insert(), properties
        )
        logger.info("Insert primary key %s", str(result.inserted_primary_key))
        return result.inserted_primary_key[0] if len(result.inserted_primary_key) else None

###################################################################
# User Interaction Commands
###################################################################


def rate_movie(conn: Connection, movie_id: int, rating: int, id: int = None) -> None:
    """ Rate movie /5. Update user rating, or new one"""

    vote_time = datetime.datetime.now()
    add_update_entry(conn, "RATINGS", id=id, movie_id=movie_id,
                     rating=rating, date=vote_time)


def add_source(conn: Connection, movie_id: int = None, id: int = None, source_id: int = None, vote: int = None, **kw) -> None:
    """ Add source to movie. Or change/add new vote . If source doesn't pre-exist add, otherwise update is properties supplied."""
    # If there are new source properties need to insert/update them
    if kw:
        source_id = add_update_entry(conn, "SOURCES", id=id, **kw)

    if movie_id is not None and id is not None and source_id is not None:
        add_update_entry(
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
    add_update_entry(conn, "ACTORS", id=id, **actor)


def save_character(conn: Connection, character: Dict, id: int = None) -> None:
    add_update_entry(conn, "CHARACTERS", id=id, **character)


def add_movie_quote(conn: Connection, id: int = None, **kw) -> None:
    """Add quote to database. If ID supplied, updates entry, else adds"""
    if kw:
        id = add_update_entry(conn, "MOVIE_QUOTE", id=id, **kw)


def add_genre(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """Add genre to database."""
    if kw:
        id = add_update_entry(conn, "GENRES", id=id, **kw)
    if movie_id is not None and id is not None:
        add_update_entry(conn, "MOVIE_GENRE", movie_id=movie_id, genre_id=id)


def add_representation(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """Add representation to database, optionally apply to movie"""
    if kw:
        id = add_update_entry(conn, "REPRESENTATIONS", id=id, **kw)
    if movie_id is not None and id is not None:
        add_update_entry(conn, "MOVIE_REPRESENTATION",
                         movie_id=movie_id, representation_id=id)


def add_relationship(conn: Connection, character_id1: int = None, character_id2: int = None, explicit: int = None, id: int = None, **kw) -> None:
    """Add relationship to database."""
    if kw:
        id = add_update_entry(conn, "RELATIONSHIPS", id=id, **kw)

    if character_id1 is not None and character_id2 is not None and id is not None:
        add_update_entry(conn, "CHARACTER_RELATIONSHIP", character_id1=character_id1,
                         character_id2=character_id2, relationship_id=id, explict=explicit)


def add_trope(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """ Add/Update new Trope Type, then optionally add relation to movie."""
    if kw:
        id = add_update_entry(conn, "TROPE_TRIGGERS", id=id, **kw)

    if movie_id is not None and id is not None:
        add_update_entry(conn, "MOVIE_TROPE_TRIGGER",
                         movie_id=movie_id, trope_trigger_id=id)


def add_intensity(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """ Add/Update new Intensity Type, then optionally add relation to movie."""
    if kw:
        add_update_entry(conn, "INTENSITIES", id=id, **kw)
    if movie_id is not None and id is not None:
        add_update_entry(conn, "MOVIE_INTENSITY",
                         movie_id=movie_id, intensity_id=id)


def add_quality(conn: Connection, id: int = None, movie_id: int = None, **kw) -> None:
    """ Add/Update new Quality Type, then optionally add relation to movie."""
    if kw:
        id = add_update_entry(conn, "QUALITIES", id=id, **kw)
    if movie_id is not None and id is not None:
        add_update_entry(conn, "MOVIE_QUALITY",
                         movie_id=movie_id, quality_id=id)
