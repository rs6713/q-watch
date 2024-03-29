import datetime
import json
import itertools
import logging
import math
import random
import re
import os
from typing import Dict, List


from currency_converter import CurrencyConverter
import coloredlogs
from flask import Flask, request
from markupsafe import escape
import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table

from qwatch.io import _create_engine
from qwatch.io.input import (
    get_entries,
    get_movie,
    _get_movie_labels
)
from qwatch.io.output import (
    add_update_entry
)
from qwatch.io.utils import (
    Aggregate,
    MovieEntries,
    MovieLabels,
    TableAggregate,
    TableJoin,
)

logger = logging.getLogger("qwatch")
loglvl = logging.INFO

logger.setLevel(loglvl)
ch = logging.StreamHandler()
ch.setLevel(loglvl)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s'
)
ch.setFormatter(formatter)
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.addHandler(ch)

coloredlogs.install(level='INFO', logger=logger)

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


# Setup DB
engine = _create_engine()
metadata = MetaData()  # bind=engine

movie_table = Table('MOVIES', metadata, )

people_table = Table('PEOPLE', metadata, )
person_ethnicity_table = Table('PERSON_ETHNICITY', metadata, )
person_disability_table = Table('PERSON_DISABILITY', metadata, )
person_role_table = Table('PERSON_ROLE', metadata, )

movie_source_table = Table('MOVIE_SOURCE', metadata, )
movie_source_vote_table = Table('MOVIE_SOURCE_VOTE', metadata, )
movie_trope_trigger_table = Table(
    'MOVIE_TROPE_TRIGGER', metadata, )
movie_tag_table = Table(
    'MOVIE_TAG', metadata, )
movie_representation_table = Table(
    'MOVIE_REPRESENTATION', metadata, )
movie_genre_table = Table('MOVIE_GENRE', metadata, )

app = Flask(__name__)

# Default Values
MOVIE_QUALITIES = ["ID", "COUNTRY", "YEAR", "LANGUAGE",
                   "BOX_OFFICE", "BUDGET", "INTENSITY", "AGE"]
MOVIE_LABELS = ["GENRE", "TYPE", "TROPE_TRIGGER", "REPRESENTATION", "TAG"]
MOVIE_LABELS_EXTRAS = {
    'TYPE': ['EXPLICIT'],
    'REPRESENTATION': ['MAIN']
}

# Create Label Mappings
LABEL_MAPPINGS = {}
with engine.begin() as conn:
    for label in [*MOVIE_LABELS, "INTENSITY", "AGE"]:
        labels, _ = get_entries(conn, F"{label}S")
        LABEL_MAPPINGS[f'{label}S'] = {
            l['ID']: l
            for l in labels
        }


def convert_to_json(d):
    return {
        k: (
            v.to_dict('records')
            if isinstance(v, pd.DataFrame) else v
        )
        for k, v in d.items()
    }


@app.route('/api/movie/labels')
def get_labels() -> Dict:

    tables = MOVIE_LABELS + ["INTENSITY", "CAREER", "ACTION", 'AGE']

    labels = {}
    with engine.begin() as conn:
        for table in tables:
            labels[f"{table}S"] = get_entries(
                conn, f"{table}S"
            )[0]

    options = [
        {'TABLE': 'MOVIES', 'ID': 'COUNTRY', 'TYPE': 'LIST'},
        {'TABLE': 'MOVIES', 'ID': 'LANGUAGE', 'TYPE': 'STRING_DISAGG'},
    ]
    with engine.begin() as conn:
        for option in options:
            vals = get_entries(
                conn, option['TABLE'], return_properties=[option['ID']])
            if option['TYPE'] == 'LIST':
                labels[f"{option['ID']}S"] = sorted(list(set(vals)))
            if option['TYPE'] == 'STRING_DISAGG':
                labels[f"{option['ID']}S"] = sorted(list(set(itertools.chain.from_iterable(
                    list(map(lambda s: s.replace(' ', '').split(','), vals))
                ))))

    return labels


@app.route('/api/characters/count', methods=["POST"])
def get_count_matching_characters() -> int:
    criteria = request.get_json().get("criteria", {})

    characters = get_matching_characters(criteria)

    return len(characters)


@app.route('/api/characters', methods=["POST"])
def get_character_list():
    """
    Get character list using posted criteria.
    Return specified properties
    """
    criteria = request.get_json().get("criteria", {})
    properties = request.get_json().get("properties", None)

    characters = get_matching_characters(criteria, properties)

    return {"characters": characters}


def get_matching_characters(criteria: Dict, properties: List[str] = None):
    """ Get charaters matching specified criteria."""
    query = MovieEntries(
        name='CHARACTERS', table='CHARACTERS',
        joins=[
            *[TableJoin(
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
                for prop in ["DISABILITY", "ETHNICITY"]],
            TableJoin(
                TableAggregate(
                    table_name=f'CHARACTER_ACTION',
                    aggs=[
                        Aggregate(f'ACTION_ID', 'ACTIONS', 'string')
                    ],
                    groups=['CHARACTER_ID']
                ),
                return_properties=['ACTIONS'],
                base_table_prop='ID', join_table_prop='CHARACTER_ID',
                isouter=True
            ),
            TableJoin(
                "PEOPLE",
                return_properties=['DOB'],
                base_table_prop="ACTOR_ID", join_table_prop='ID',
                isouter=False
            ),
            TableJoin(
                "MOVIES",
                return_properties=['YEAR'],
                base_table_prop="MOVIE_ID", join_table_prop="ID",
                isouter=False
            )
        ]
    )
    with engine.begin() as conn:
        characters = get_entries(
            conn, query.table,
            return_properties=properties,
            joins=query.joins,
            return_format="listdict",
            **criteria
        )
        if properties is None or len(properties) > 1:
            characters = characters[0]

        logger.info(
            "Found %d characters matching criteria: %s",
            len(characters), str(criteria)
        )

    # If associated actor has DOB, calculate approximate character age.
    for character in characters:
        logger.info(character['DOB'])
        if character.get('DOB', None) is not None and len(character['DOB']) >= 4 and character['DOB'][:4].isdecimal():
            character['APPROX_AGE'] = int(character['YEAR']) - \
                int(character['DOB'][:4])
    return characters


def get_matching_people(criteria: Dict, properties: List[str] = None) -> List[Dict]:
    """ Get People matching specified criteria."""
    query = MovieEntries('PEOPLE', 'PEOPLE', joins=[
        *[
            TableJoin(
                TableAggregate(
                    table_name=f'PERSON_{prop}',
                    aggs=[
                        Aggregate(f'{prop}_ID', prop, 'string')
                    ],
                    groups=["PERSON_ID"] +
                    (["MOVIE_ID"] if prop == "ROLE" else []),
                    criteria=(None if prop == "ROLE" else {
                              "IS_CHARACTER": False})
                ),
                return_properties=[prop] +
                (["MOVIE_ID"] if prop == "ROLE" else []),
                base_table_prop='ID', join_table_prop='PERSON_ID',
                isouter=(False if prop == "ROLE" else True)
            )
            for prop in ["DISABILITY", "ETHNICITY", "ROLE"]
        ]
    ])

    with engine.begin() as conn:
        people = get_entries(
            conn, query.table,
            return_properties=properties,
            joins=query.joins,
            return_format="listdict",
            **criteria
        )
        print(people)
        if properties is None or len(properties) > 1:
            people = people[0]
    logger.info(
        "Found %d people matching criteria: %s, properties %s",
        len(people), str(criteria), str(properties)
    )

    return people


@app.route('/api/people', methods=["POST"])
def get_people_list():
    """
    Get people list using posted criteria.
    Return specified properties
    """
    criteria = request.get_json().get("criteria", {})
    properties = request.get_json().get("properties", None)

    people = get_matching_people(criteria, properties)

    return {"people": people}


@app.route('/api/people/count', methods=["POST"])
def get_count_matching_people() -> int:
    """ Get count of people that match criteria."""
    criteria = request.get_json().get("criteria", {})

    people = get_matching_people(criteria)

    return len(people)


def get_matching_movies(criteria: Dict, properties: List[str] = None) -> List[int]:
    """
    Get properties of movies that match criteria
    - qualities: values on MOVIES entries, e.g. YEAR, BOX_OFFICE
    - labels: many-to_many labels assigned to movies e.g. representations

    """
    logger.info(
        "Retrieving movies that match criteria: %s",
        str(criteria)
    )
    if properties is None:
        return_properties = None
    else:
        return_properties = list(set([*properties, "ID"]))

    query = MovieEntries('MOVIES', 'MOVIES', joins=[
        j for j in
        [
            # Table joins for all LABEL's attached to MOVIES through many-to-many mappings
            *[
                TableJoin(
                    TableAggregate(
                        table_name=f'MOVIE_{prop}',
                        aggs=[
                            Aggregate(f'{prop}_ID', f'{prop}S', 'string'),
                            *[
                                Aggregate(e, f'{prop}S_{e}', 'string')
                                for e in MOVIE_LABELS_EXTRAS.get(prop, [])
                            ]
                        ],
                        groups=["MOVIE_ID"],
                        criteria={
                            e: criteria[f'{prop}S'][e]
                            for e in MOVIE_LABELS_EXTRAS.get(prop, [])
                            if f'{prop}S' in criteria and e in criteria[f'{prop}S'] and criteria[f'{prop}S'][e] is not None
                        }
                    ),
                    return_properties=[f'{prop}S', *[
                        f'{prop}S_{e}'
                        for e in MOVIE_LABELS_EXTRAS.get(prop, [])
                    ]],
                    base_table_prop='ID', join_table_prop='MOVIE_ID',
                    isouter=True
                )
                for prop in MOVIE_LABELS
            ],
            # Average and number of ratings attached to movie
            TableJoin(
                TableAggregate(
                    table_name="RATINGS",
                    aggs=[
                        Aggregate('RATING', 'AVG_RATING', 'mean'),
                        Aggregate('RATING', 'NUM_RATING', 'count')
                    ],
                    groups=["MOVIE_ID"]
                ),
                return_properties=["AVG_RATING", "NUM_RATING"],
                base_table_prop='ID', join_table_prop='MOVIE_ID',
                isouter=True
            ),
            # Join Image entry to default image
            TableJoin(
                "MOVIE_IMAGE",
                return_properties=["FILENAME", "CAPTION"],
                base_table_prop='DEFAULT_IMAGE', join_table_prop='ID',
                isouter=True
            ),
            # Images to attach to movie
            TableJoin(
                TableAggregate(
                    table_name="MOVIE_IMAGE",
                    aggs=[
                        Aggregate('ID', 'IMAGES', 'string')
                    ],
                    groups=["MOVIE_ID"]
                ),
                return_properties=["IMAGES"],
                base_table_prop="ID", join_table_prop="MOVIE_ID",
                isouter=False
            ),
            # ID of sources to attach to movie
            TableJoin(
                TableAggregate(
                    table_name="MOVIE_SOURCE",
                    aggs=[
                        Aggregate('ID', 'SOURCES', 'string')
                    ],
                    groups=["MOVIE_ID"]
                ),
                return_properties=["SOURCES"],
                base_table_prop="ID", join_table_prop="MOVIE_ID",
                isouter=True
            )
            # Filter table joins if for properties not in criteria or return_properties
        ] if any([p in (properties or []) or p in criteria.keys() for p in (j.return_properties or [])])
    ])

    # criteria_qualities = {
    #     k: v for k, v in criteria.get("qualities", {}).items()
    #     if k in MOVIE_QUALITIES
    # }
    # criteria_labels = {
    #     label: label_criteria
    #     for label, label_criteria in criteria.get("labels", {}).items()
    #     if label in MOVIE_LABELS
    # }

    # criteria = {
    #     k: v for k, v in criteria.items()
    #     if k in [*MOVIE_QUALITIES, *MOVIE_LABELS]
    # }

    with engine.begin() as conn:
        movies = get_entries(
            conn, query.table,
            return_properties=return_properties,
            joins=query.joins,
            return_format="listdict",
            # **criteria_qualities,
            # **criteria_labels
            **criteria
        )
        # Not just a list has been returned
        if return_properties is None or len(return_properties) > 1:
            movies = movies[0]

    logger.info('Got entries - all movies matching criteria')
    # Filter movies that don't have associated character types
    if "CHARACTERS" in criteria:
        movie_ids = get_matching_characters(
            {**criteria["CHARACTERS"], "MOVIE_ID": [movie["ID"]
                                                    for movie in movies]},
            properties=["MOVIE_ID"]
        )
        movies = [
            movie for movie in movies
            if (movie["ID"] if isinstance(movie, dict) else movie) in movie_ids
        ]

    # Filter movies if have associated people matching people criteria.
    if "PEOPLE" in criteria:
        movie_ids = get_matching_people(
            {**criteria["PEOPLE"], "MOVIE_ID": [movie["ID"]
                                                for movie in movies]},
            properties=["MOVIE_ID"]
        )
        logger.info("Matching PEOPLE Movie IDS %s", str(movie_ids))
        movies = [
            movie for movie in movies
            if (movie["ID"] if isinstance(movie, dict) else movie) in movie_ids
        ]

    # Perform Post-Processing on properties
    if return_properties is not None and "FILENAME" in return_properties:
        logger.info('Fetching movie captions, filename for thumbnail image')
        with engine.begin() as conn:
            for movie in movies:
                if movie["FILENAME"] is None:

                    # Set as first image
                    images = get_entries(
                        conn, "MOVIE_IMAGE",
                        return_properties=["FILENAME", "CAPTION"],
                        MOVIE_ID=movie["ID"]
                    )[0]
                    if len(images):
                        movie["FILENAME"] = images[0]["FILENAME"]
                        movie["CAPTION"] = images[0]["CAPTION"]

    if return_properties is None or 'SOURCES' in return_properties:
        logger.info('Getting sources')
        source_query = MovieEntries('MOVIE_SOURCE', 'MOVIE_SOURCE', joins=[
            TableJoin(
                "SOURCES",
                return_properties=["LABEL", "URL",
                                   "REGION", "IMAGE", "LGBT_RUN"],
                base_table_prop='SOURCE_ID', join_table_prop='ID',
                isouter=False
            ),
            TableJoin(
                TableAggregate(
                    table_name="MOVIE_SOURCE_VOTE",
                    aggs=[
                        Aggregate('ID', 'VOTES', 'string')
                    ],
                    groups=["MOVIE_SOURCE_ID"]
                ),
                return_properties=["VOTES"],
                base_table_prop="ID", join_table_prop="MOVIE_SOURCE_ID",
                isouter=True
            )
        ])

        for movie in movies:
            if movie.get('SOURCES', []):
                with engine.begin() as conn:
                    movie['SOURCES'] = get_entries(
                        conn, source_query.table,
                        return_properties=None,
                        joins=source_query.joins,
                        return_format="listdict",
                        ID=(movie['SOURCES'])
                    )[0]
                    for source in (movie['SOURCES'] or []):
                        source['VOTES'] = get_entries(
                            conn, 'MOVIE_SOURCE_VOTE',
                            ID=(source['VOTES'] or []),
                            return_properties=['VOTE', 'DATE', 'ID']
                        )[0]
                        source['LGBT_RUN'] = int(source['LGBT_RUN'])

    if return_properties is None or "IMAGES" in return_properties:
        logger.info('Fetching movie images')
        for movie in movies:
            if movie.get('IMAGES', []):
                with engine.begin() as conn:
                    movie["IMAGES"] = get_entries(
                        conn, "MOVIE_IMAGE",
                        ID=(movie["IMAGES"] or [])
                    )[0]

    for movie in movies:
        if (return_properties is None or "AVG_RATING" in return_properties) and (movie.get("AVG_RATING", None) is None or np.isnan(movie["AVG_RATING"])):
            movie["AVG_RATING"] = 0.0
        if (return_properties is None or "NUM_RATING" in return_properties) and (movie.get("NUM_RATING", None) is None or np.isnan(movie["NUM_RATING"])):
            movie["NUM_RATING"] = 0
        for label in MOVIE_LABELS:
            if ((return_properties is None or f"{label}S" in return_properties) and movie.get(f"{label}S", None) is not None):
                movie[f"{label}S"] = [
                    {
                        **LABEL_MAPPINGS[f"{label}S"][i],
                        **{
                            e: movie[f'{label}S_{e}'][index]
                            for e in MOVIE_LABELS_EXTRAS.get(label, [])
                            if f'{label}S_{e}' in movie
                        }
                    }
                    for index, i in enumerate(movie[f"{label}S"])
                ]
        for label in ["INTENSITY", "AGE"]:
            if return_properties is None or label in return_properties:
                movie[label] = LABEL_MAPPINGS[f"{label}S"][movie[label]]

    logger.info(f'Returning movies, {type(movies)} {len(movies)}')
    return movies


@ app.route('/api/movies/count', methods=["POST"])
def get_count_matching_movies() -> int:
    """
    With filters, get count of movies that match request.

    {
        criteria:
        groupby: e.g. COUNTRY, YEAR, GENRE
    }
    """
    criteria = request.get_json().get("criteria", {})
    groups = request.get_json().get("groups", {})

    props = list(set(itertools.chain.from_iterable(groups.values())))

    movies = get_matching_movies(criteria, properties=["ID", *props])

    na_maps = {
        'BOX_OFFICE_USD': -1,
        'BUDGET_USD': -1,
        'BOX_OFFICE': '',
        'BUDGET': '',
    }
    for movie in movies:
        for col in na_maps:
            if col in movie:
                movie[col] = movie[col] if movie[col] is not None else na_maps[col]

    logger.info(movies[0].keys())

    if not groups:
        return convert_to_json({'TOTAL': len(movies)})

    counts = {'TOTAL': len(movies)}
    for group_name, group_cols in groups.items():
        new_movies = []
        for movie in movies:
            if len(group_cols) > 1:
                try:
                    movie['group'] = list(itertools.product(
                        *[
                            list(set([
                                _['LABEL'] if isinstance(_, dict)
                                else _
                                for _ in movie[c]
                            ])) if isinstance(
                                movie[c], list) else [movie[c]]
                            for c in group_cols
                        ]
                    ))
                    movie['group'] = [
                        ', '.join([str(_) for _ in g])
                        for g in movie['group']
                    ]
                except Exception as e:
                    logger.info(str(e))
                    logger.info(str(group_cols))
                    logger.info(str([movie[c] for c in group_cols]))
                    raise e
            else:
                if movie[group_cols[0]] is not None:
                    movie['group'] = (
                        movie[group_cols[0]]
                        if isinstance(movie[group_cols[0]], list)
                        else [movie[group_cols[0]]]
                    )
                    movie['group'] = [
                        p['LABEL'] if isinstance(p, dict) else p for p in movie['group']
                    ]
                else:
                    movie['group'] = None

            if movie['group'] is not None:
                for p in set(movie['group']):
                    new_movies.append(
                        {
                            'ID': movie['ID'],
                            'group': p
                        }
                    )

        counts[group_name] = pd.DataFrame(new_movies).groupby(
            by='group').ID.count().to_dict()

    return convert_to_json(counts)


@ app.route('/api/movie/featured')
def get_movie_featured():
    """ Return movie that is associated with ID."""
    this_week = (
        datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    )

    logger.info('Getting featured movie occuring in week %s',
                this_week.strftime('%Y-%m-%d'))

    with engine.begin() as conn:
        featured_movie = get_entries(
            conn,
            'FEATURED_MOVIE',
            return_properties=[
                'MOVIE_ID',
                'DESCRIP'
            ],
            START_WEEK=this_week
        )[0]
        if not len(featured_movie):
            logger.info('No featured movie matching start_week %s',
                        this_week.strftime('%Y-%m-%d'))
            return {}

        properties = [
            "TITLE", "SUMMARY",
            "YEAR",
            "FILENAME", "CAPTION",
            "AVG_RATING", "NUM_RATING",
            "GENRES", "TYPES", "AGE", "RUNTIME",
            "TAGS", "LANGUAGE", "COUNTRY",
            "REPRESENTATIONS"
        ]
        movie_props = get_matching_movies(
            {'ID': featured_movie[0]['MOVIE_ID']},
            properties=properties
        )[0]
        if not len(movie_props):
            logger.warning('No movie matching featured movie id: %d',
                           featured_movie[0]['MOVIE_ID'])
            return {}

        print(movie_props)
        movie_props = {
            **movie_props,
            'DESCRIP': featured_movie[0]['DESCRIP']
        }
    return convert_to_json(movie_props)


@ app.route('/api/movie/<int:movie_id>')
def get_movie_by_id(movie_id: int):
    """ Return movie that is associated with ID."""
    movie_id = int(movie_id)

    movie = get_matching_movies(
        dict(ID=movie_id),
        properties=[
            'TITLE',
            'YEAR',
            'IMAGES',
            'AVG_RATING',
            'NUM_RATING',
            'LANGUAGE',
            'BIO',
            'SUMMARY',
            'INTENSITY',
            'GENRES',
            'RUNTIME',
            'AGE',
            'TYPES',
            'TAGS',
            'IMDB_ID',
            'COUNTRY',
            'SOURCES',
            'TROPE_TRIGGERS',
            'TRAILER',
            'REPRESENTATIONS',
            'BOX_OFFICE_USD', 'BUDGET_USD',
        ]
    )[0]

    return convert_to_json(movie)


def convert_to_usd(obj, key):

    if key not in ['BUDGET', 'BOX_OFFICE']:
        raise ValueError(
            'Conversion to USD can only be on currency-based columns')
    if obj[key] is None or len(obj[key]) == 0:
        return 0

    currency_maps = {
        '$': 'USD',
        '£': 'GBP',
        '€': 'EUR'
    }
    currency = [c for c in currency_maps if c in obj[key]]
    if len(currency) == 1:
        c = CurrencyConverter()
        return c.convert(
            int(re.sub(r'[^0-9]', '', obj[key])),
            currency_maps[currency[0]],
            'USD',
            # f'{obj["YEAR"]}-01-01'
        )

    else:
        logger.warning('Failed to convert to USD COLUMN %s: %s',
                       key, str(obj[key]))
        return 0


@ app.route('/api/movies', methods=["POST"])
def get_movie_list():
    """
    Get movie list using posted criteria.

    """
    criteria = request.get_json().get("criteria", {})
    properties = request.get_json().get("properties", None)
    sort = request.get_json().get("sort", None)
    index = request.get_json().get("index", None)

    logger.info(
        "Getting movies with sort %s, index %d, against criteria:\n%s",
        (sort or ''), (index or 0), str(criteria)
    )

    results_per_index = 12

    idProperties = ['ID']
    if sort is not None:
        idProperties += [sort[0]]

    movies = get_matching_movies(criteria, properties=idProperties)
    logger.info(f'Got idmovies {len(movies)}')
    n_indexes = math.ceil(len(movies) / results_per_index)

    # Sort movies according to sort
    if sort is not None and sort:

        movies = sorted(
            movies,
            key=lambda movie: movie[sort[0]],
            reverse=sort[1] == -1
        )

    n_matches = len(movies)

    if index is not None:
        if index > n_indexes or index < 1:
            # TODO How to do error messages
            return json.dumps({'success': False}), 400

        movies = movies[
            (index - 1) * results_per_index: index * results_per_index
        ]

    if properties is None:
        properties = [
            "TITLE",
            "YEAR",
            "BIO",
            "FILENAME",
            "CAPTION",
            "AVG_RATING",
            "NUM_RATING",
            "GENRES",
            "TYPES"
        ]
    matchIds = (
        [m['ID'] for m in movies]
        if len(idProperties) > 1
        else movies
    )
    movies = get_matching_movies(
        {'ID': matchIds}, properties=properties)
    logger.info(f'Got movies {len(movies)}')
    if len(movies) == 0:
        return {"data": [], "n_indexes": 0, "n_matches": 0}

    # Sort movies according to sort
    if sort is not None and sort:

        movies = sorted(
            movies,
            key=lambda movie: movie[sort[0]],
            reverse=sort[1] == -1
        )

    na_maps = {
        'BOX_OFFICE_USD': 0,
        'BUDGET_USD': 0,
        'BOX_OFFICE': '',
        'BUDGET': '',
    }
    for movie in movies:
        for col in na_maps.keys():
            if col in movie:
                if movie[col] is None or (not isinstance(movie[col], str) and np.isnan(movie[col])):
                    movie[col] = na_maps[col]

    return {"data": movies, "n_indexes": n_indexes, "n_matches": n_matches}

    # if request.method == 'POST':
    #     genre = request.form.get('genre')
    # else:
    #     genre = request.args.get('genre')


@ app.route('/api/gif/random', methods=['GET'])
def get_random_gif():
    """ Get random gif. """
    with engine.begin() as conn:
        joins = [
            TableJoin(
                'MOVIES',
                return_properties=['TITLE', 'YEAR'],
                base_table_prop='MOVIE_ID', join_table_prop='ID',
                isouter=False
            )
        ]
        gifs = get_entries(
            conn,
            "MOVIE_IMAGE",
            joins=joins,
            return_properties=[
                'TITLE', 'MOVIE_ID', 'CAPTION', 'FILENAME', 'YEAR'
            ],
            FILENAME={"TYPE": "LIKE", "VALUE": [".gif", ".webp"]}
        )[0]
        chosen_random_gif = random.choice(gifs)

        return convert_to_json(chosen_random_gif)


@ app.route('/api/movie/random', methods=["POST"])
def get_random_movie():
    """ Return information of random movie. """
    properties = request.get_json().get("properties", None)

    with engine.begin() as conn:
        movie_ids = get_entries(
            conn, "MOVIES", return_properties=["ID"]
        )
        chosen_movie_id = random.choice(movie_ids)

        if len(properties) == 1 and properties[0] == "ID":
            return {'ID': chosen_movie_id}

        logger.info("Returning random movie: %d", chosen_movie_id)
        movie = get_movie(
            conn, chosen_movie_id, properties=properties
        )
    return convert_to_json(movie)


@ app.route('/api/movie/rating', methods=["POST"])
def save_movie_rating() -> int:
    """ Save rating for movie. """
    movie_id = int(request.get_json()['movie_id'])
    rating = int(request.get_json()['rating'])
    movie_rating_id = request.get_json()['movie_rating_id'] or -1
    if movie_rating_id is not None:
        movie_rating_id = int(movie_rating_id)

    logger.info(
        "Saving movie rating for movie %d, rating %d, existing rating? %s",
        movie_id, rating, str(movie_rating_id)
    )

    if not (rating <= 5 and rating >= 1):
        return json.dumps({'success': False}), 400

    with engine.begin() as conn:
        print(get_entries(
            conn, "MOVIES", ID=movie_id)[0])
        movie_exists = len(get_entries(
            conn, "MOVIES", ID=movie_id)[0]) == 1
        if not movie_exists:
            return json.dumps({'success': False}), 400

        movie_rating_id = add_update_entry(
            conn,
            "RATINGS",
            ID=movie_rating_id,
            MOVIE_ID=movie_id,
            RATING=rating,
            DATE=datetime.datetime.now()
        )
    return json.dumps({'success': True, "movie_rating_id": movie_rating_id}), 200


@ app.route('/api/source/vote', methods=['POST'])
def save_movie_source_vote() -> int:
    """ Up/down vote a movie source. """
    movie_source_id = int(request.get_json()['movie_source_id'])
    vote = int(request.get_json()['vote'])
    movie_source_vote_id = request.get_json().get('movie_source_vote_id', -1)
    if movie_source_vote_id == -1:
        movie_source_vote_id = None
    if movie_source_vote_id is not None:
        movie_source_vote_id = int(movie_source_vote_id)

    logger.info(
        'Saving vote %d for movie source %d, with existing vote id %d',
        vote, movie_source_id, movie_source_vote_id
    )

    if not (vote in [-1, 0, 1]):
        return json.dumps({'success': False}), 400

    with engine.begin() as conn:
        movie_source_exists = len(get_entries(
            conn, "MOVIE_SOURCE", ID=movie_source_id)[0]) == 1
        if not movie_source_exists:
            return json.dumps({'success': False}), 400

        movie_source_vote_id = add_update_entry(
            conn,
            "MOVIE_SOURCE_VOTE",
            ID=movie_source_vote_id,
            MOVIE_SOURCE_ID=movie_source_id,
            VOTE=vote,
            DATE=datetime.datetime.now()
        )
    return json.dumps({'success': True, "movie_source_vote_id": movie_source_vote_id}), 200


if __name__ == '__main__':
    # run app in debug mode on port 5000
    print('Production: ', os.environ.get('PRODUCTION', True),
          ' PORT: ', int(os.environ.get('PORT', 8080)))
    app.run(
        debug=not os.environ.get('PRODUCTION', False),
        host='0.0.0.0', port=int(os.environ.get('PORT', 8080))
    )
