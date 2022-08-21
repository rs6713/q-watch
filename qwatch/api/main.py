from typing import Dict, List

from flask import Flask, request
from markupsafe import escape
from sqlalchemy import MetaData, Table


from qwatch.utils import _create_engine
from qwatch.io.input import (
    get_entries,
    get_movie,
    _get_movie_labels
)
from qwatch.io.output import (
    add_update_entry
)

# Setup DB
engine = _create_engine()
metadata = MetaData(bind=engine)

movie_table = Table('MOVIES', metadata, autoload=True)

people_table = Table('PEOPLE', metadata, autoload=True)
person_ethnicity_table = Table('PERSON_ETHNICITY', metadata, autoload=True)
person_disability_table = Table('PERSON_DISABILITY', metadata, autoload=True)
person_role_table = Table('PERSON_ROLE', metadata, autoload=True)

movie_source_table = Table('MOVIE_SOURCE', metadata, autoload=True)
movie_source_vote_table = Table('MOVIE_SOURCE_VOTE', metadata, autoload=True)
movie_trope_trigger_table = Table(
    'MOVIE_TROPE_TRIGGER', metadata, autoload=True)
movie_representation_table = Table(
    'MOVIE_REPRESENTATION', metadata, autoload=True)
movie_genre_table = Table('MOVIE_GENRE', metadata, autoload=True)

app = Flask(__name__)

# Default Values
MOVIE_QUALTIIES = ["COUNTRY", "YEAR", "LANGUAGE",
                   "BOX_OFFICE", "BUDGET", "INTENSITY", "AGE"]
MOVIE_LABELS = ["GENRE", "TYPE", "TROPE_TRIGGER", "REPRESENTATION"]


def convert_to_json(d):
    return {
        k: v.to_dict('records') if isinstance(v, pd.DataFrame) else v
    }


@app.route('/api/count/people', methods=["POST"])
def get_count_matching_people() -> int:
    ethnicty_id = escape(request.form.get("ethnicity_id"))
    disability_id = escape(request.form.get("disability_id"))


@app.route('/api/count/characters', methods=["POST"])
def get_count_matching_characters() -> int:
    """
    {
        criteria: MAIN
        groupby: GENRE, ETHNCIITY,
    }
    {
        criteria: brunettes that pursue a lighter haired person
    }
    """
    pass


def get_matching_people(criteria: Dict, movie_id: List[str] = None, properties: List[str] = None) -> List[int]:
    """
    Get people ids that match criteria
    """
    if properties is None:
        return_properties = ["ID"]
    else:
        return_properties = list(set([*properties, "ID"]))

    with engine.begin() as conn:
        # If getting characters
        if criteria.get("IS_CHARACTER", 0):

        else:
            if criteria.get("ROLE", None) is not None:
                get_entries(
                    conn, "PERSON_ROLE", MOVIE_ID=movie_id, ROLE_ID=criteria.get("ROLE")
                )


def get_matching_movies(criteria: Dict, properties: List[str] = None) -> List[int]:
    """
    Get movie ids of movies that match criteria
    - qualities: values on MOVIES entries, e.g. YEAR, BOX_OFFICE
    - labels: many-to_many labels assigned to movies e.g. representations
    - writers: writers associated with 
    """
    if properties is None:
        return_properties = ["ID"]
    else:
        return_properties = list(set([*properties, "ID"]))

    criteria_qualities = {
        k: v for k, v in criteria.get("qualities", {}).items()
        if k in MOVIE_QUALTIIES
    }
    criteria_labels = {
        label: label_criteria
        for label, label_criteria in criteria.get("labels", {}).items()
        if label in MOVIE_LABELS
    }

    with engine.begin() as conn:
        movies, _ = get_entries(
            conn, "MOVIES", **criteria_qualities, return_properties=return_properties)

        for label in criteria_labels:
            if not len(movies):
                return []
            # Just getting labels by value, then using INCLUDE/EXCLUDE to determine if
            # LABEL should exist for movie, or not exist.
            matching_movies, _ = get_entries(conn, f"MOVIE_{label}",
                                             **{f'{label}_ID': criteria_labels[label]["VALUE"]})
            matching_movie_ids = [movie["MOVIE_ID"]
                                  for movie in matching_movies]

            if criteria_labels[label]["TYPE"] == "INCLUDE":
                movies = [
                    movie for movie in movies
                    if movie["ID"] in matching_movie_ids
                ]
            if criteria_labels[label]["TYPE"] == "EXCLUDE":
                movies = [
                    movie for movie in movies
                    if movie["ID"] not in matching_movie_ids
                ]

    # Filter movies if have associated people matching people criteria.
    if "PEOPLE" in crtieria:
        movie_ids = get_matching_people(
            criteria["PEOPLE"],
            movie_id=[movie["ID"] for movie in movies],
            properties=["MOVIE_ID"]
        )
        movies = [
            movie for movie in movies
            if movie["ID"] in movie_ids
        ]
    if len(return_properties) == 1:
        return [movie[return_properties[0]] for movie in movies]

    return [{k: v for k, v in movie.items() if k in properties} for movie in movies]


@app.route('/api/count/movie', methods=["POST"])
def get_count_matching_movies() -> int:
    """
    With filters, get count of movies that match request.

    {
        criteria:
        groupby: e.g. COUNTRY, YEAR, GENRE
    }
    """
    criteria = request.get_json()
    movie_ids = get_matching_movie_ids(criteria, properties=["ID"])

    return len(movie_ids)


@app.route('/api/movie/<int:id>')
def get_movie_by_id(movie_id: int):
    """ Return movie that is associated with ID."""
    movie_id = escape(movie_id)

    with engine.begin() as conn:
        movie = get_movie(
            conn, ID=movie_id
        )

    return convert_to_json(movie)


@app.route('/api/movielist', methods=["POST"])
def get_movie_list():
    """
    Get movie list using posted criteria.

    """
    criteria = request.get_json().get("criteria", {})
    properties = request.get_json().get("properties", None)
    movie_ids = get_matching_movies(criteria, properties=["ID"])

    if properties is None:
        properties = [
            "TITLE",
            "YEAR",
            "BIO",
            "DEFAULT_IMAGE",
            "RATING"
        ]

    movies = []
    for movie_id in movie_ids:
        movies.append(
            get_movie(
                movie_id,
                properties=properties
            )
        )

    return movies

    # if request.method == 'POST':
    #     genre = request.form.get('genre')
    # else:
    #     genre = request.args.get('genre')


@app.route('api/movie/random')
def get_random_movie():
    """ Return information of random movie. """
    properties = request.get_json().get("properties", {})
    _ =


@app.route('api/movie/rating/', methods=["POST"])
def save_movie_rating() -> int:
    """ Save rating for movie. """
    movie_id = request.form.get('movie_id')
    rating = request.form.get('rating')
    movie_rating_id = request.form.get('movie_rating_id')

    if not (isinstance(rating, int) and rating <= 5 and rating >= 1):
        return json.dumps({'success': False}), 400
    if not (isinstance(movie_id, int)):
        return json.dumps({'success': False}), 400

    with engine.begin() as conn:
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
            DATE=datetime.datetine.now()
        )
    return json.dumps({'success': True, "movie_rating_id": movie_rating_id}), 200


@app.route('api/source/vote/')
def save_movie_source_vote() -> int:
    """ Up/down vote a movie source. """
    movie_source_id = request.form.get('movie_source_id')
    vote = request.form.get('vote')
    movie_source_vote_id = request.form.get('movie_source_vote_id')

    if not (isinstance(vote, int) and vote in [-1, 0, 1]):
        return json.dumps({'success': False}), 400
    if not (isinstance(movie_source_id, int)):
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
            DATE=datetime.datetine.now()
        )
    return json.dumps({'success': True, "movie_source_vote_id": movie_source_vote_id}), 200


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
