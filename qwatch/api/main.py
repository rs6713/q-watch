from flask import Flask
from markupsafe import escape

app = Flask(__name__)


@app.route('/api/movie/<int:id>')
def get_movie_by_id(id: int):
    id = escape(id)
