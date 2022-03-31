#%%
from IPython.display import display
import sqlalchemy

from qwatch.io.input import (
  get_characters,
  get_genres,
  get_representations,
  get_tropes
)

#%%
engine = sqlalchemy.create_engine('mssql+pyodbc://localhost/Q-Watch?driver=SQL+Server+Native+Client+11.0')
#engine = sqlalchemy.create_engine('mssql+pyodbc://localhost/master')
with engine.connect() as cur_conn:
  for movie_id in [None, 3]:
    df = get_representations(cur_conn, movie_id=movie_id)
    display(df)
    df = get_genres(cur_conn, movie_id=movie_id)
    display(df)
    df = get_characters(cur_conn, movie_id=movie_id)
    display(df)
    df = get_tropes(cur_conn, movie_id=movie_id)
    display(df)

# %%
