""" Central Scraper GUI. """
from functools import partial

import spacy
import sqlalchemy
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
from tkinter.font import Font

import webbrowser

from qwatch.io import _create_engine
from qwatch.io.input import (
  get_representations,
  get_tropes,
  get_genres,
  get_movies_ids,
  _get_movie_properties,
  get_movie
)
from qwatch.scrape.images import download_images
from qwatch.scrape.wikipedia import get_movie_details
from qwatch.gui.images import ImagePanel
from qwatch.gui.menus import MenuMultiSelector, ChecklistBox
from qwatch.gui.people import PeoplePanel

nlp_model = spacy.load('en_core_web_md')

# class MovieLoader(tk.Frame):
#   def __init__(self, parent, **kwargs):
#     tk.Frame.__init__(self, parent, **kwargs)
    
#     self.movie_title_entry = tk.Entry(
#       self.topFrame,
#       bg="white", fg="black", width=40
#     )
#     # Searchbar for Movie
#     self.search = tk.Button(
#       self.topFrame,
#       text="Search Movie",
#       #height=1, #width=10,
#       command=partial(self.get_movie_info, limit=3)
#     )
#     self.movie_title_entry.pack(side="left", fill="both", expand=True)
#     self.search.pack(side="right", padx=(5, 0))#fill="x", expand=False


#     self.movieSelected = tk.StringVar()
#     self.movieSelected.set("Select Pre-Existing Movie")
#     self.movieSelector = tk.OptionMenu(self.movieSelectorContainer, self.movieSelected, *self.movies.values())
#     self.movieSelector.pack(side="left", expand=True, fill=tk.X)
#     movieSelectorButton = tk.Button(self.movieSelectorContainer, text="Edit", command=self.edit_movie)
#     movieSelectorButton.pack(side="right")

#     self.movieSelectorContainer.grid(
#       column=2, row=0, rowspan=1, columnspan=4
#     )


class MovieWindow():

  def get_movie_properties(self):
    """ Getting possible movie properties """
    engine = _create_engine()
    with engine.connect() as conn:
      self.representations = get_representations(conn)
      self.tropes = get_tropes(conn)
      self.genres = get_genres(conn)
      self.movies = get_movies_ids(conn)

      #selfgi.qualities = get_qualties(conn)

  def configure_root(self):
    """ Configure properties of app window."""
    self.root = tk.Tk()
    self.root.title("Q-Watch Movie Loader")

  def configure_menu(self):
    """ Menu Operations Available."""
    self.menubar = tk.Menu(self.root)
    self.fileMenu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label='File', menu=self.fileMenu)
    self.fileMenu.add_command(label='New', command=self.search_movie)
    self.fileMenu.add_command(label='Open', command=self.open_movie)
    self.fileMenu.add_command(label='Save', command=self.save_movie)
    self.fileMenu.add_separator()
    self.fileMenu.add_command(label='Exit', command=self.root.destroy)
  
  def open_movie(self):
    open_movie_popup = tk.Toplevel(pady=5, padx=5)
    open_movie_popup.wm_title("Open Movie")

    movie_selected = tk.StringVar()
    movie_selected.set("Select Movie")
    movie_selector = tk.OptionMenu(
      open_movie_popup, movie_selected, *self.movies.values()
    )
    movie_selector.config(width=30)
    movie_selector.pack(side="left", padx=(0, 5), fill=tk.X, expand=True)

    def edit_movie():
      selected_movie_id = [k for k, v in self.movies.items() if v == movie_selected.get()]
      if len(selected_movie_id):
        self.load_movie(movie_id=selected_movie_id[0])
        open_movie_popup.destroy()

    movie_selector_button = tk.Button(
      open_movie_popup, 
      text="Open",
      command=edit_movie,
      padx=5, pady=2
    )
    movie_selector_button.pack(side="right")

  def check_title_matches(self, title):
    potential_matches = [
      (movie_id, movie_title)
      for movie_id, movie_title in self.movies.items()
      if nlp_model(movie_title).similarity(nlp_model(title)) > 0.9
    ]
    return potential_matches

  def load_movie_warning(self, movies, title):
    edit_movie_popup = tk.Toplevel(pady=5, padx=5)
    edit_movie_popup.wm_title("Warning! Movie matches pre-existing movies")

    txt = tk.Label(
      edit_movie_popup,
      wraplength=300,
      text=f"Similar Movies to '{title}' pre-exist. Either edit or continue to create new"
    )
    txt.grid(row=0, column=0, columnspan=2, sticky="ew")

    for i, (movie_id, movie_title) in enumerate(movies):
      movie_label = tk.Label(edit_movie_popup, text=movie_title)
      movie_label.grid(row=i+1, column=0, padx=(0, 5))

      def load_movie(movie_id):
        def func():
          self.load_movie(movie_id=movie_id)
          edit_movie_popup.destroy()
        return func

      movie_button = tk.Button(
        edit_movie_popup, text="Edit",
        command=load_movie(movie_id=movie_id)
      )
      movie_label.grid(row=1+i, column=0, sticky=tk.W)
      movie_button.grid(row=1+i, column=1, sticky=tk.E, padx=(5, 0))

    continue_button = tk.Button(
      edit_movie_popup, text="Continue",
      command=partial(self.load_movie, title),
      padx=2, pady=2
    )
    continue_button.grid(column=1, sticky=tk.E, row=len(movies)+1)
  def search_movie(self):
    """Pop up Window to search for new movie."""
    new_movie_popup = tk.Toplevel(pady=5, padx=5)
    new_movie_popup.wm_title("Search Movie")

    # Movie Title
    movie_title_entry = tk.Entry(
      new_movie_popup,
      bg="white", fg="black", width=40
    )
    movie_title_entry.pack(side="left")

    def load_movie():
      title = movie_title_entry.get()
      print(title)
      title_matches = self.check_title_matches(title)
      if len(title_matches) > 0:
        self.load_movie_warning(title_matches, title)
      else:
        self.load_movie(movie_title=title)
      new_movie_popup.destroy()

    # Searchbar for Movie
    search_button = tk.Button(
      new_movie_popup,
      text="Search",
      command=load_movie,
      padx=5, pady=2
    )
    search_button.pack(side="left", padx=(5, 0))

  def load_movie(self, movie_title=None, movie_id=None, movie_year=None, limit=1):
    movie_info = {}
    
    if movie_title is not None:
      movie_info["title"] = movie_title
      # Get movie images
      image_dirs = download_images(movie_title, limit=limit)
      movie_info["images"] = image_dirs[0][movie_title]

      # Get movie details
      details = get_movie_details(movie_title)

      self.current_movie = {
        **self.current_movie,
        **movie_info,
        **details
      }
    
    # Load movie to edit
    elif movie_id is not None:
      engine = _create_engine()
      with engine.connect() as conn:
        self.current_movie = get_movie(conn, movie_id)
      
    self.update_contents()

  def save_movie(self):
    pass

  def update_contents(self):

    if "url" in self.current_movie:
      #self.url = tk.Label(self.shortFrame, text="Wiki URL")
      fr = tk.Frame(self.root)

      self.url = tk.Button(
        fr,
        text="Wiki URL",
        width=10, height=1,
        command=lambda: webbrowser.open_new(self.current_movie["url"])
      )
      self.url.pack(side="left")
      fr.grid(column=0, columnspan=2, row=7+len(self.shortFrames))
      self.shortFrames.append(fr)

    props = ["age", "summary", "year", "language", "country", "running_time"]
    print("Update_contents: \n", self.current_movie)
    for prop in props:
      if prop in self.current_movie:
        if hasattr(self, prop):
          #getattr(self, prop).delete('0', tk.END)
          getattr(self, prop).insert(tk.END, self.current_movie[prop])
        else:
          print(f"No {prop} console item")
    
    if "images" in self.current_movie:
      self.imagePanel.loadImages(self.current_movie["images"])



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
  def alert(err_type, msg):
    if err_type == "warning":
      messagebox.showinfo('Movie Submission Warning', msg)
      messagebox.askyesno("askyesno", "Continue submitting Movie?")
    if err_type == "error":
      messagebox.showerror("showerror", "Movie Entry is Invalid:\n" + error_msg)

  def __init__(self):
    self.current_movie = {}

    self.get_movie_properties()
    self.configure_root()
    self.configure_menu()

    ###################################################
    # Scrolled Text for Wiki Summary
    ###################################################
    self.summaryLabel = tk.Label(self.root, text="Summary")# justify=tk.LEFT, anchor="w"
    self.summary = scrolledtext.ScrolledText(
      self.root, height=10, width=50,
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

    self.opinion.grid(row=6, column=0, columnspan=2, padx=5, sticky="ew")
    self.opinionLabel.grid(row=5, column=0, columnspan=2, sticky = tk.W, padx=5)

    self.summaryLabel.grid(row=1, column=0, columnspan=2, sticky = tk.W, padx=5)
    self.summary.grid(row=2, column=0, columnspan=2, padx=5)

    self.bioLabel.grid(row=3, column=0, columnspan=2, sticky = tk.W, padx=5)
    self.bio.grid(row=4, column=0, columnspan=2, padx=5, sticky="ew")

    self.root.update()
    summaryHeight = self.summary.winfo_height()
    self.represent_checklist = ChecklistBox(
      self.root, "Representations", self.representations, height=summaryHeight, width=150
    )
    self.trope_checklist = ChecklistBox(
      self.root, "Tropes", self.tropes, height=summaryHeight, width=150
    )
    self.genre_checklist = ChecklistBox(
      self.root, "Genres", self.genres, height=summaryHeight, width=150
    )

    self.shortFrames = []
    shortProps = {
      "rating": 1,
      "year": 4,
      "age": 3,
      "language": 3,
      "country": 3,
      "running_time": 3
    }
    for i, (prop, width) in enumerate(shortProps.items()):
      if i %3 == 0:
        self.shortFrames.append(tk.Frame(self.root))

      #setattr(self, prop+"Label", tk.Label(self.shortFrame, text=prop))
      setattr(self, prop+"Label", tk.LabelFrame(self.shortFrames[int(i//3)], text=prop))
      setattr(self, prop, tk.Entry(getattr(self, prop+"Label")))

      getattr(self, prop+"Label").pack(
        side="left",
        fill=tk.X, # fill horizontally
        expand=True,
        pady=1, padx=1
      )
      #setattr(self, prop, tk.Entry(self.shortFrame, height=1, width=width))
      getattr(self, prop).pack(
        side="top",
        fill=tk.X, #fill horizontally
        expand=True,
        pady=1, padx=1
      )
    
    self.imagePanel = ImagePanel(self.root)
    self.imagePanel.grid(
      column=3, row=3, columnspan=6, rowspan=6,
      sticky="ewns"
    )

    # ###############################
    # # Menu to Edit Existing Movie
    # ###############################
    # self.movieSelectorContainer = tk.Frame(self.root)
    # self.movieSelected = tk.StringVar()
    # self.movieSelected.set("Select Pre-Existing Movie")
    # self.movieSelector = tk.OptionMenu(self.movieSelectorContainer, self.movieSelected, *self.movies.values())
    # self.movieSelector.pack(side="left", expand=True, fill=tk.X)
    # movieSelectorButton = tk.Button(self.movieSelectorContainer, text="Edit", command=self.edit_movie)
    # movieSelectorButton.pack(side="right")

    # self.movieSelectorContainer.grid(
    #   column=2, row=0, rowspan=1, columnspan=4
    # )



    # Place interactive elements in root
    
    for i, frame in enumerate(self.shortFrames):
      frame.grid(row=7+i, column=0, columnspan=2, rowspan=1, sticky="ew", padx=5)
    
    self.genre_checklist.grid(column=5, row=1, rowspan=2)
    self.trope_checklist.grid(column=6, row=1, rowspan=2)
    self.represent_checklist.grid(column=7, row=1, rowspan=2)
    
    ##############################################################
    # CharacterFrame for People/Characters/Relationships in Movie
    ##############################################################

    self.personFrame = PeoplePanel(self.root)
    self.personFrame.grid(
      column=0, row=10, columnspan=8, rowspan=2,
      sticky="ewns"
    )

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
  