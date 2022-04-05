""" Central Scraper GUI. """
from IPython.display import display
import sqlalchemy
import tkinter as tk
from tkinter import messagebox, scrolledtext

import webbrowser

from qwatch.io import _create_engine
from qwatch.io.input import (
  get_representations,
  get_tropes,
  get_genres
)
from qwatch.scrape import images
from qwatch.scrape.wikipedia import get_movie_details

class MovieWindow():

  def get_movie_properties(self):
    """ Getting possible movie properties """
    engine = _create_engine()
    with engine.connect() as conn:
      self.representations = get_representations(conn)
      self.tropes = get_tropes(conn)
      self.genres = get_genres(conn)
      #self.qualities = get_qualties(conn)

  def configure_root(self):
    """ Configure properties of app window."""
    self.root = tk.Tk()
    #self.root.configure(bg="#f2c7ee")
    self.root.title("Q-Watch Movie Loader")
    self.root.geometry('500x500')

  def configure_menu(self):
    """ Menu Operations Available."""
    self.menubar = tk.Menu(self.root)
    self.fileMenu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label='File', menu=self.fileMenu)
    self.fileMenu.add_command(label='Save', command=None)
    self.fileMenu.add_separator()
    self.fileMenu.add_command(label='Exit', command=self.root.destroy)

  def get_movie_info(self, limit=1):
    movie_info = {}
    movie_title = self.movie_title_entry.get()

    # TODO Check if movie already exists in db

    movie_info["title"] = movie_title

    # Get movie images
    image_dirs = images.download(movie_title, limit=limit)
    movie_info["images"] = image_dirs[0][movie_title]

    # Get movie details
    details = get_movie_details(movie_title)
    print(details)

    self.movie_info = movie_info

    if "url" in details:
      #self.url = tk.Label(self.shortFrame, text="Wiki URL")

      self.url = tk.Button(
        self.shortFrame,
        text="Wiki URL",
        width=10, height=1,
        command=lambda e: webbrowser.open_new(details["url"])
      )
      self.url.pack(side="left")
      # self.url.bind("<Button-1>", lambda e: webbrowser.open_new(details["url"]))
  
  @staticmethod
  def openUrl(url):
    def func(*args):
      webbrowser.open_new(url)
    return func

  @staticmethod
  def create_list(window, name, items):
    label = tk.Label(
      window,
      text=name,
      width=10, height=2
    )
    scroll_bar = tk.Scrollbar(window)

    item_list = tk.Listbox(window, yscrollcommand = scroll_bar.set, width=20, selectmode= "multiple")
    for i, item in items.iterrows():
      item_list.insert(tk.END, item.LABEL)
    
    scroll_bar.config(command=item_list.yview)

    return label, item_list, scroll_bar

  @staticmethod
  def alert(warning):
    messagebox.showinfo('Movie Submission Warning', warning)
    messagebox.askyesno("askyesno", "Continue submitting Movie?")
  
  @staticmethod
  def error(error_msg):
    messagebox.showerror("showerror", "Movie Entry is Invalid:\n" + error_msg)


  def __init__(self, movie_info = None):
    if movie_info is None:
      self.movie_info = {}
    else:
      self.movie_info = movie_info

    self.get_movie_properties()
    self.configure_root()
    self.configure_menu()

    self.topFrame = tk.Frame(self.root)
    # Movie Title
    self.movie_title_entry = tk.Entry(
      self.topFrame,
      width=40,
      bg="white", fg="black"
    )
    # Searchbar for Movie
    self.search = tk.Button(
      self.topFrame,
      text="Search Movie",
      width=10, height=1,
      command=self.get_movie_info
    )
    self.movie_title_entry.pack(side="left")
    self.search.pack(side="left")

    self.trope_label, self.trope_list, self.trope_scroll = self.create_list(self.root, "Tropes", self.tropes)
    self.represent_label, self.represent_list, self.represent_scroll = self.create_list(self.root, "Represent", self.representations)
    self.genre_label, self.genre_list, self.genre_scroll = self.create_list(self.root, "Genres", self.genres)

    self.characterFrame = tk.Frame(self.root, bg="white")
    characterLabel = tk.Label(self.characterFrame, text="Actor/Characters")
    characterLabel.pack(side="top")

    ###################################################
    # Scrolled Text for Wiki Summary
    ###################################################
    self.summaryLabel = tk.Label(self.root, text="Summary")
    self.summary = scrolledtext.ScrolledText(
      self.root, width=40, height=10,
      wrap=tk.WORD
    )

    self.bioLabel = tk.Label(self.root, text="Bio")
    self.bio = tk.Text(
      self.root, height=3, width=40
    )
    self.opinionLabel = tk.Label(self.root, text="My Opinion")
    self.opinion = tk.Text(
      self.root, height=3, width=40
    )

    self.shortFrame = tk.Frame(self.root)

    self.ratingLabel = tk.Label(self.shortFrame, text="Rating")
    self.ratingLabel.pack(side="left", fill="both", expand=True)
    self.rating = tk.Text(self.shortFrame, height=1, width=2)
    self.rating.pack(side="left", fill="both", expand=True)
    self.yearLabel = tk.Label(self.shortFrame, text="Year")
    self.yearLabel.pack(side="left", fill="both", expand=True)
    self.year = tk.Text(self.shortFrame, height=1, width=4)
    self.year.pack(side="left", fill="both", expand=True)
    self.ageRatingLabel = tk.Label(self.shortFrame, text="Age Rating")
    self.ageRatingLabel.pack(side="left", fill="both", expand=True)
    self.ageRating = tk.Text(self.shortFrame, height=1, width=2)
    self.ageRating.pack(side="left", fill="both", expand=True)


    # Place interactive elements in root
    self.topFrame.grid(row=0, column=0, columnspan=9)
    self.shortFrame.grid(row=7, column=0, columnspan=2)
    self.characterFrame.grid(column=11, row=1, rowspan=6)

    self.trope_label.grid(column=5, row=1, columnspan=2)
    self.trope_list.grid(column=5, row=2, rowspan=2)
    self.trope_scroll.grid(row=2, column=6, rowspan=2)
    self.represent_label.grid(column=7, row=1, columnspan=2)
    self.represent_list.grid(column=7, row=2, rowspan=2)
    self.represent_scroll.grid(row=2, column=8, rowspan=2)
    self.genre_label.grid(column=9, row=1, columnspan=2)
    self.genre_list.grid(column=9, row=2, rowspan=2)
    self.genre_scroll.grid(row=2, column=10, rowspan=2)

    self.opinion.grid(row=6, column=0, columnspan=2)
    self.opinionLabel.grid(row=5, column=0, columnspan=2)

    self.summaryLabel.grid(row=1, column=0, columnspan=2)
    self.summary.grid(row=2, column=0, columnspan=2)

    self.bioLabel.grid(row=3, column=0, columnspan=2)
    self.bio.grid(row=4, column=0, columnspan=2)


    self.root.config(menu=self.menubar)
    self.root.mainloop()

if __name__ == "__main__":
  MovieWindow()






  

  #text_box.get(tk.START, tk.END)

  #entry.insert(0, text)


  # Run Tkinter event loop, listens for events, button clicks, blocks other code running til window closes.

  # trope_label = tk.Label(
  #   text="Tropes",
  #   width=10, height=2
  # )
  # trope_label.grid(row=1, column=7)
  # trope_scroll_bar = tk.Scrollbar(window)
  # trope_scroll_bar.grid(row=2, column=8, rowspan=1)

  # trope_list = tk.Listbox(window, yscrollcommand = trope_scroll_bar.set, width=20, selectmode= "multiple")
  # for i, trope in tropes.iterrows():
  #   trope_list.insert(tk.END, trope.LABEL)
  # trope_list.grid(column=7, row=2, rowspan=1)

  # trope_scroll_bar.config(command=trope_list.yview)


  # trope_states = [tk.BooleanVar() for _ in range(tropes.shape[0])]
  # for i, trope in tropes.iterrows():
  #   chk = tk.Checkbutton(window, text=trope.LABEL, var=trope_states[i])
  #   #chk.grid(column=0, row=i)
  #   chk.grid(row=i+2, column=7, pady=2)

  ##################################################
  # Create Genre Dropdown
  ##################################################
  # genre_label = tk.Label(
  #   text="Genres",
  #   width=10, height=2
  # )
  # genre_label.grid(row=1, column=5)
  # genre_states = [tk.BooleanVar() for _ in range(genres.shape[0])]
  # for i, genre in genres.iterrows():
  #   chk = tk.Checkbutton(window, text=genre.LABEL, var=genre_states[i])
  #   #chk.grid(column=0, row=i)
  #   chk.grid(row=i+2, column=5, pady=2)
  