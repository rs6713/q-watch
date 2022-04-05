""" Central Scraper GUI. """
from IPython.display import display
import sqlalchemy
import tkinter as tk
from tkinter import messagebox, scrolledtext



from qwatch.io import _create_engine
from qwatch.io.input import (
  get_representations,
  get_tropes,
  get_genres
)
from qwatch.scrape import images
from qwatch.scrape.wikipedia import get_movie_details

def main():
  #####################################################
  # Get Movie categories
  #####################################################
  engine = _create_engine()
  with engine.connect() as conn:
    representations = get_representations(conn)
    tropes = get_tropes(conn)
    genres = get_genres(conn)

    print(genres)
  window = tk.Tk(
    #bg="#f2c7ee"
  )
  window.title("Q-Watch Movie Loader")
  window.geometry('500x500')

  # Label widget
  # welcome = tk.Label(
  #   text="Add Movie",
  #   width=10, height=2
  # )
  # welcome.pack()


  # Movie Title
  movie_title_entry = tk.Entry(
    width=40,
    bg="white", fg="black"
  )
  movie_title_entry.grid(row=0, column=0, pady=2)

  def get_movie_all(limit=1):
    movie_info = {}
    movie_title = movie_title_entry.get()

    movie_info["title"] = movie_title

    # Get movie images
    image_dirs = images.download(movie_title, limit=limit)
    movie_info["images"] = image_dirs[0][movie_title]

    # Get movie details
    details = get_movie_details(movie_title)
    print(details)


  search = tk.Button(
    text="Search Movie",
    width=10, height=1,
    command=get_movie_all
  )
  search.grid(row=0, column=1, pady=2)


  ##################################################
  # Create Genre Dropdown
  ##################################################
  genre_label = tk.Label(
    text="Genres",
    width=10, height=2
  )
  genre_label.grid(row=1, column=5)
  genre_states = [tk.BooleanVar() for _ in range(genres.shape[0])]
  for i, genre in genres.iterrows():
    chk = tk.Checkbutton(window, text=genre.LABEL, var=genre_states[i])
    #chk.grid(column=0, row=i)
    chk.grid(row=i+2, column=5, pady=2)
  
  ###################################################
  # Create Represent Dropdown
  ###################################################
  represent_label = tk.Label(
    text="Representations",
    width=10, height=2
  )
  represent_label.grid(row=1, column=6)
  represent_states = [tk.BooleanVar() for _ in range(representations.shape[0])]
  for i, represent in representations.iterrows():
    chk = tk.Checkbutton(window, text=represent.LABEL, var=represent_states[i])
    #chk.grid(column=0, row=i)
    chk.grid(row=i+2, column=6, pady=2)

  ###################################################
  # Create Trope Dropdown
  ###################################################
  trope_label = tk.Label(
    text="Tropes",
    width=10, height=2
  )
  trope_label.grid(row=1, column=7)
  trope_states = [tk.BooleanVar() for _ in range(tropes.shape[0])]
  for i, trope in tropes.iterrows():
    chk = tk.Checkbutton(window, text=trope.LABEL, var=trope_states[i])
    #chk.grid(column=0, row=i)
    chk.grid(row=i+2, column=7, pady=2)
  

  def alert(warning):
    messagebox.showinfo('Movie Submission Warning', warning)
    messagebox.askyesno("askyesno", "Continue submitting Movie?")
  #alert("Bad title")
  
  def error(error_msg):
    messagebox.showerror("showerror", "Movie Entry is Invalid:\n" + error_msg)
  #alert("Invalid Movie Entry")


  ###################################################
  # Scrolled Text for Wiki Summary
  ###################################################
  summary = scrolledtext.ScrolledText(
    window, width=40, height=10,
    wrap=tk.WORD
  )
  summary.insert(tk.INSERT, 'Summary for Article')
  summary.grid(row=1, column=0)

  

  #text_box.get(tk.START, tk.END)

  #entry.insert(0, text)


  # Run Tkinter event loop, listens for events, button clicks, blocks other code running til window closes.
  window.mainloop()

if __name__ == "__main__":
  main()