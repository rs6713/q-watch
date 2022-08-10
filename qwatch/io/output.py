""" Functions to save data to SQL Server."""
import datetime
import logging
import numbers
import os
from pathlib import Path
import shutil
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import (
    and_,
    case,
    create_engine,
    delete,
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

from qwatch.io.input import get_entries
from qwatch.utils import describe_obj

logger = logging.getLogger(__name__)

SCHEMA = "dbo"


def delete_movie(conn: Connection, movie_id: int) -> None:
    """
    Delete all information associated with movie with id [movie_id]

    Params
    ------
    movie_id: int
        ID of movie in MOVIES table.

    Steps
    -----
    Remove:
        - genres, tropes, representations, types, images, quotes, sources
        - person roles
        - characters
        - character relationships
        - character actions
    """
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
        if props == "SOURCE" and len(removed_entries):
            remove_entry(conn, "MOVIE_SOURCE_VOTE",
                         MOVIE_SOURCE_ID=removed_entries)

    ##################################################
    # Remove People, Characters, Actions
    ##################################################
    remove_entry(conn, "PERSON_ROLE", MOVIE_ID=movie_id)
    character_ids = remove_entry(
        conn, "CHARACTERS", MOVIE_ID=movie_id, return_prop="ID")
    character_ids = [
        int(i) for i in character_ids
    ]

    if len(character_ids):
        remove_entry(conn, "CHARACTER_RELATIONSHIPS",
                     CHARACTER_ID1=character_ids)
        remove_entry(conn, "CHARACTER_RELATIONSHIPS",
                     CHARACTER_ID2=character_ids)
        remove_entry(conn, "CHARACTER_ACTIONS", CHARACTER_ID=character_ids)


def preprocess_movie(movie: Dict) -> Dict:
    """
    Pre-Process Movie Information, suitable for storage.

    Steps
    -----
    - Convert applicable movie traits to int format
    - Copy movie images to movie-pictures dir
      Format [TITLE]_[YEAR]-[NUMERIC_ID].ext

    Returns
    -------
    Dict
        Pre-processed movie Object
    """
    logger.info(
        "Performing movie cleaning --> Converting entries to correct type")
    for k in movie:
        try:
            if movie[k] == -1:
                movie[k] = None
        # Handle exception in case movie[k] is dataframe
        except Exception as e:
            continue
        if k in ["YEAR", "RUNTIME", "BOX_OFFICE", "BUDGET"]:
            num_prop = [c for c in movie[k] if c.isnumeric()]
            if len(num_prop):
                movie[k] = int(''.join(num_prop))
            else:
                movie[k] = None

    ###################################################
    # If an image is new, copy it to movie-pictures dir
    # Update its pathname in (to-be-stored) db record
    ###################################################
    if movie["IMAGES"] is not None and len(movie["IMAGES"]):
        img_dir = os.path.join(
            Path(__name__).parent.parent.parent,
            "website", "src", "static", "movie-pictures")
        img_name = movie["TITLE"].lower().replace(
            " ", "-") + "_" + str(movie["YEAR"])

        # Determine next image numeric id
        existing_imgs = [
            int(f.split(".")[0].split("-")[-1])
            for f in os.listdir(img_dir)
            if img_name in f
        ]
        if existing_imgs:
            existing_img_n = max(existing_imgs) + 1
        else:
            existing_img_n = 0

        for image in movie["IMAGES"]:
            try:
                # If image does not pre-exist copy to movie-pictures dir
                if image["ID"] is None or not image["ID"] or image["ID"] == -1:
                    ext = image["FILENAME"].split(".")[1]
                    dst = os.path.join(
                        img_dir,
                        f"{img_name}-{existing_img_n:03d}.{ext}"
                    )
                    shutil.copyfile(image["FILENAME"], dst)
                    image["FILENAME"] = img_name + \
                        f"-{existing_img_n:03d}.{ext}"
                    existing_img_n += 1
                    logger.info("Copying image to %s", image["FILENAME"])
            except Exception as e:
                logger.warning(
                    "Failed to copy over image: %s to %s",
                    image["FILENAME"], dst
                )
                continue

    return movie


def update_entry_by_id_list(conn: Connection, table_name: str, id_list: List[int], **match_criteria) -> None:
    """
    Update lists of ids that are associated with [match_criteria] in table .._[PROP].

    Steps
    -----
    - Leaves rows that do not match criteria untouched
    - Keeps rows that match criteria, whose [PROP]_ID is in id_list
    - Deletes rows that match criteria, whose [PROP]_ID is not in id_list
    - Inserts rows, with match criteria, for each new [PROP]_ID

    Example
    -------
    table_name = 'PERSON_ROLE'
    id_list = [3,4]
    match_criteria = {'PERSON_ID': 2, 'MOVIE_ID': 1}

    Original DB
    ID | PERSON_ID | MOVIE_ID | ROLE_ID
    -----------------------------------
    1    2           1          2 --> Deleted
    2    3           1          3 --> Untouched (no match)
    3    2           1          3 --> Kept
    ...
    New Entries
    8    2           1          4

    Returns
    -------
    List[int]
        ID's of rows associated with match criteria, post db insertions/deletions
    """
    logger.info("update_entry_by_id_list Saving/Updating  %d entries in %s",
                len((id_list or [])), table_name)
    prop = table_name.split("_")[-1]

    existing_entries, _ = get_entries(conn, table_name, **match_criteria)
    new_ids = []

    # If there are new entries to add.
    if id_list is not None and len(id_list):
        # Remove deleted entries, that exist in db but not id_list
        removed_entries = [
            entry["ID"] for entry in existing_entries
            if entry[f"{prop}_ID"] not in id_list
        ]
        logger.info("Deleting %d entries in %s",
                    len(removed_entries), table_name)
        for entry_id in removed_entries:
            remove_entry(conn, table_name, ID=entry_id)

        # Update / Add New Entries
        logger.info("Adding %d entries", len(id_list or []))
        for entry in id_list:
            # Allows for overlapping properties
            new_entry = {f"{prop}_ID": entry, **match_criteria}
            new_ids += [
                add_update_entry(conn, table_name, **new_entry)
            ]
    else:
        logger.info(
            "Removing all entries in %s that match %s",
            table_name, describe_obj(match_criteria)
        )
        # Remove all existing entries
        remove_entry(conn, table_name, **match_criteria)

    return new_ids


def update_entry_list(conn: Connection, table_name: str, entry_list: List[Dict], **match_criteria) -> List[int]:
    """
    Update lists of entries that are associated with [match_criteria] in table [MOVIE]_[PROP].

    Steps
    -----
    - Leaves rows that do not match criteria untouched
    - Updates rows with specified ID's, with entry values
    - Deletes rows that match criteria, whose ID is not in any of the entries in entry_list
    - Inserts row entrys, auto-generating new ID, for those with no ID specified.

    Example
    -------
    table_name = 'MOVIE_TROPE_TRIGGER'
    entry_list = [{'ID':3, 'TROPE_TRIGGER_ID':7}, {'ID':None, 'TROPE_TRIGGER_ID':2}]
    match_criteria = {'MOVIE_ID': 1}

    Original DB
    ID | MOVIE_ID | TROPE_TRIGGER_ID
    -----------------------------------
    1    3          2                   --> Untouched (no match)
    2    1          4                   --> Deleted
    3    1          7                   --> Kept
    ...
    New Entries
    8    1           2          

    Returns
    -------
    List[int]
        ID's of rows associated with match criteria, post db insertions/deletions
    """
    logger.info("Saving/Updating %d entries in %s",
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
        logger.info(
            "Removing all entries in %s associated with %s",
            table_name,
            describe_obj(match_criteria)
        )
        remove_entry(conn, table_name, **match_criteria)

    return new_ids


def save_movie(conn: Connection, movie: Dict) -> int:
    """
    Save/Update movie. Returns int of created movie id

    Raises
    ------
    Exception if movie creation process fails.
    If it is a new movie recording, partially completed entry will be deleted from db.
    """
    logger.info("Saving movie: %s, pre-existing id: %d",
                movie["TITLE"], movie["ID"])
    MOVIE_EXISTS = movie.get("ID", -1) != -1

    ############################################
    # Clean movie information
    # Data preprocessing, Copy over Images Files
    ############################################
    movie = preprocess_movie(movie)

    ######################
    # Insert movie into DB
    ######################
    movie_id = add_update_entry(conn, "MOVIES", **movie)

    try:
        ###########################################################
        # Add/update tables of properties associated with the movie
        # Many to many relationships in MOVIE_[prop]
        ###########################################################
        update_props = [
            "SOURCE",
            "TROPE_TRIGGER",
            "GENRE",
            "REPRESENTATION",
            "TYPE",
            "IMAGE",
        ]
        for prop in update_props:
            _ = update_entry_list(
                conn, f"MOVIE_{prop}", movie[f"{prop}S"], MOVIE_ID=movie_id
            )

        ############################################################
        # Add/Update People associated with movie
        # Includes inserting many-many people properties into tables
        # Roles, disabilities, ethnciities.
        ############################################################
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
                if prop == "ROLE":
                    _ = update_entry_by_id_list(
                        conn, f"PERSON_{prop}", person.get(prop, []),
                        PERSON_ID=person["ID"], MOVIE_ID=movie_id
                    )
                else:
                    _ = update_entry_by_id_list(
                        conn, f"PERSON_{prop}", person.get(prop, []),
                        PERSON_ID=person["ID"], IS_CHARACTER=0
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
                    _ = update_entry_by_id_list(
                        conn, f"PERSON_{prop}", character.get(prop, []),
                        PERSON_ID=character["ID"], IS_CHARACTER=1,
                    )

        ######################################
        # Save Quotes after character mappings
        ######################################
        logger.debug("Character ID Mappings %s", str(character_id_mappings))
        if movie.get("QUOTES", None) is not None and len(movie["QUOTES"]):
            for quote in movie["QUOTES"]:

                quote["CHARACTER_ID"] = character_id_mappings[quote["CHARACTER_ID"]]

            _ = update_entry_list(
                conn, f"MOVIE_QUOTE", movie["QUOTES"], MOVIE_ID=movie_id
            )

        logger.info("Adding %d character actions", len(
            (movie["CHARACTER_ACTIONS"] or [])))
        if movie["CHARACTER_ACTIONS"] is not None and len(movie["CHARACTER_ACTIONS"]):
            logger.debug("Pre-map Movie Character Actions: \n%s",
                         str(movie["CHARACTER_ACTIONS"]))
            movie["CHARACTER_ACTIONS"] = [
                {**ca,
                    "CHARACTER_ID": character_id_mappings[ca["CHARACTER_ID"]]}
                for ca in movie["CHARACTER_ACTIONS"]
            ]
            logger.debug("Post-map Movie Character Actions: \n%s",
                         str(movie["CHARACTER_ACTIONS"]))
            for character_action in movie["CHARACTER_ACTIONS"]:
                _ = update_entry_by_id_list(
                    conn, "CHARACTER_ACTIONS", character_action.get(
                        "ACTION_ID", []),
                    CHARACTER_ID=character_action["CHARACTER_ID"],
                )

        logger.info("Adding %d character relationship",
                    len((movie["RELATIONSHIPS"] or [])))
        if movie["RELATIONSHIPS"] is not None and len(movie["RELATIONSHIPS"]):
            for r in movie["RELATIONSHIPS"]:
                if not(
                        isinstance(character["ID"], numbers.Number) and len(str(character["ID"])) < 15):
                    r["ID"] = None

            movie["RELATIONSHIPS"] = [
                {
                    **r,
                    "CHARACTER_ID1": character_id_mappings[r["CHARACTER_ID1"]],
                    "CHARACTER_ID2": character_id_mappings[r["CHARACTER_ID2"]]
                }
                for r in movie["RELATIONSHIPS"]
            ]
            logger.debug(describe_obj(movie["RELATIONSHIPS"]))
            _ = update_entry_list(
                conn, "CHARACTER_RELATIONSHIPS", movie["RELATIONSHIPS"],
                CHARACTER_ID1=existing_characters
            )
    except Exception as e:
        logger.error(
            "Error while saving movie %s, %s.\n %s",
            movie_id, movie["TITLE"], str(e)
        )
        if not MOVIE_EXISTS:
            logger.error(
                "Cancelling movie creation process, and deleting all references")
            delete_movie(conn, movie_id)

            img_dir = os.path.join(
                Path(__name__).parent.parent.parent,
                "website", "src", "static", "movie-pictures"
            )
            # Remove moved images
            if movie.get("IMAGES", None) is not None:
                for img in movie["IMAGES"]:
                    if img.get("ID", None) is None:
                        logger.error(
                            "Removing img %s, moved to movie-pictures", img["FILENAME"])
                        os.remove(
                            os.path.join(
                                img_dir,
                                img["FILENAME"]
                            )
                        )
        raise e

    return movie_id


def remove_entry(conn: Connection, table_name: str, return_prop=None, **properties) -> Optional[List]:
    """
    Delete entry from table [table_name], that matches properties.

    Params
    ------
    table_name: str
        Name of table
    return_prop: str
        Properties of removed entries to return.
    properties: dict
        Table {col:val} to determine entry matches

    Returns
    -------
    (Optional) Specified Property of deleted row entries in table.
    """
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

    query = table.select().where(
        and_(
            *[
                table.c[key] == val if not isinstance(
                    val, (np.ndarray, list)) else table.c[key].in_(list(val))
                for key, val in properties.items()
            ]
        )
    )
    deleted_entries = pd.DataFrame([
        _._mapping for _ in conn.execute(query).fetchall()
    ], columns=conn.execute(query).keys())

    # Return list of return_prop, that represent items deleted
    if return_prop is not None:
        results = deleted_entries[return_prop].values

    # Handle case where FILENAME in dir
    if table == "MOVIE_IMAGE":
        query = select(table.FILENAME).where(
            and_(
                *[
                    table.c[key] == val if not isinstance(
                        val, (list, np.ndarray)) else table.c[key].in_(list([
                            int(v) for v in val]))
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

    delete_query = delete(table).where(
        and_(
            *[
                table.c[key] == val if not isinstance(
                    val, (np.ndarray, list)) else table.c[key].in_(list([int(v) for v in val]))
                for key, val in properties.items()
            ]
        )
    )
    conn.execute(delete_query)

    logger.info("Deleted %d entries matching %s from table %s.",
                deleted_entries.shape[0], str(properties), table_name)

    return results


def add_update_entry(conn: Connection, table_name: str, ID: int = None, **properties) -> int:
    """
    Add/Update entry in specified table [table_name]. Return generated/existing id.

    Params
    ------
    conn: SQLAlchemy Connection
    table_name: str
        Table to update entry / add entry to
    ID: int
        (Optional) If supplied, specifies the entry to update with properties
        If not supplied, create new entry in table. Auto-generating ID.
    properties: Dict
        Column-Value Pairs to insert in row

    Returns
    -------
    int: ID of inserted/updated row
    """
    table = Table(
        table_name, MetaData(), schema=SCHEMA, autoload_with=conn
    )

    columns = [
        k for k in conn.execute(table.select()).keys()
        if k != "ID"
    ]

    # Remove properties not in table columns
    if not all([k.upper() in columns for k in properties]):
        logger.debug(
            "WARNING: %s columns not found in table %s",
            ", ".join([k for k in properties if k not in columns]),
            table_name
        )
    properties = {k: v for k, v in properties.items() if k in columns}

    # Entry already exists, has valid ID in table. Update
    if ID != -1 and ID is not None and ID:
        logger.debug("Updating entry %d in %s:\n%s", ID,
                     table_name, describe_obj(properties))
        conn.execute(update(table).where(table.c.ID == ID).values(properties))
        return ID
    # Else insert new entry into table.
    else:
        logger.debug("Inserting entry to %s\n%s",
                     table_name, describe_obj(properties))
        properties = {c: properties.get(c, None) for c in columns}
        result = conn.execute(
            table.insert(), properties
        )
        logger.debug("Produced primary key %s",
                     str(result.inserted_primary_key))
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
