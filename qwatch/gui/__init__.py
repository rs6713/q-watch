""" Central Scraper GUI. """
from functools import partial

from IPython.display import display
from PIL import Image, ImageTk
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
)
from qwatch.scrape import images
from qwatch.scrape.wikipedia import get_movie_details

class MenuMultiSelector(tk.Menubutton):
  def __init__(self, parent, name, options, **kwargs):
    tk.Menubutton.__init__(
      self,
      parent,
      text=name,
      relief=tk.RAISED,
      **kwargs
    )
    menu = tk.Menu(self, tearoff=0)
    self["menu"] = menu
    self.configure(menu=menu)
    self.menu = menu

    self.options = {}
    for _, option in options.iterrows():
        var = tk.IntVar()
        label = f"{option.LABEL} - {option.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in option.index else option.LABEL
        self.menu.add_checkbutton(label=label, variable=var)
        options[option.ID] = var

  def get_selected_options(self):

    return [
      option_id for option_id, checked in self.options.items()
      if checked.get()
    ]

class PeoplePanel(tk.Frame):
  def __init__(self, parent, people=None):

    

    tk.Frame.__init__(self, parent)
    self.notebook = ttk.Notebook(self, height=300)
    self.personPage = tk.Frame(self.notebook)
    self.characterPage = tk.Frame(self.notebook)
    self.relationshipPage = tk.Frame(self.notebook)

    self.notebook.add(self.personPage, text="Personnel")
    self.notebook.add(self.characterPage, text="Characters")
    self.notebook.add(self.relationshipPage, text="Relationships")

    self.notebook.pack(expand=1, fill="both")

    personHeader = tk.Frame(self.personPage)
    personHeader.pack(side="top", padx=5, pady=5, fill=tk.X)
    tk.Label(personHeader, text="Insert People working on movie").pack(side="left", padx=(0, 10))
    tk.Button(personHeader, text="+", command=self.create_person).pack(
      side="left", pady=5, padx=5
    )
    self.personContainer = tk.Frame(self.personPage, highlightbackground="black", highlightthickness=2)
    self.personContainer.pack(
      side="top", fill="both", expand=True
    )

    self.get_people_properties()

  def create_person(self, person=None):
    if person is None:
      person = {}

    newPerson = tk.Toplevel(pady=5, padx=5)
    newPerson.wm_title("Create Person")
    #newPerson = tk.Frame(win)

    # First name
    tk.Label(newPerson, text="First Name").grid(column=0, row=0, sticky=tk.W)
    firstname = tk.Entry(newPerson, width=30)
    firstname.focus()
    firstname.grid(column=1, row=0, sticky=tk.W, padx=(0, 10))
    if "FIRST_NAME" in person:
      firstname.insert(0, person.FIRST_NAME)

    # Last Name
    tk.Label(newPerson, text="Last Name").grid(column=0, row=1, sticky=tk.W)
    lastname = tk.Entry(newPerson, width=30)
    lastname.grid(column=1, row=1, sticky=tk.W, padx=(0, 10))
    if "LAST_NAME" in person:
      lastname.insert(0, person.LAST_NAME)

    # DOB
    tk.Label(newPerson, text="DOB").grid(column=0, row=2, sticky=tk.W)
    dob = tk.Entry(newPerson, width=30)
    dob.grid(column=1, row=2, sticky=tk.W, padx=(0, 10))
    if "DOB" in person:
      lastname.insert(0, person.DOB)
    
    def save_person():
      # TODO create person from all forms
      # save to overall dict, 
      # clear and regenerate personnel notebook page
      newPerson.destroy()

    save_button = tk.Button(newPerson, text="Save", width=10, pady=2, command=save_person)
    save_button.grid(column=3, padx=(20, 0), sticky=tk.E, row=0)

    exit_button = tk.Button(newPerson, text="Cancel", width=10, pady=2, command=newPerson.destroy)
    exit_button.grid(column=3, padx=(20, 0), sticky=tk.E, row=1)

    button_frame = tk.Frame(newPerson)
    button_frame.grid(column=0, row=3, pady=(10, 0), rowspan=1, columnspan=4, sticky="ew")

    role_menu = MenuMultiSelector(button_frame, "Roles", self.roles)
    role_menu.pack(side="left", fill=tk.X, expand=True)

    sexuality_menu = MenuMultiSelector(button_frame, "Sexuality", self.sexualities)
    sexuality_menu.pack(side="left", fill=tk.X, expand=True)

    gender_menu = MenuMultiSelector(button_frame, "Gender", self.genders)
    gender_menu.pack(side="left", fill=tk.X, expand=True)

    ethnicity_menu = MenuMultiSelector(button_frame, "Ethnicity", self.ethnicities)
    ethnicity_menu.pack(side="left", fill=tk.X, expand=True)

    bio = tk.Text(
      newPerson, height=3, width=5
    )
    #bio.grid_propagate(False)
    bio.grid(row=4, pady=(5, 0), column=0, columnspan=4, sticky="ew")
    
    newPerson.grid_columnconfigure(0, weight=1)
    newPerson.grid_rowconfigure(0, weight=1)

  def create_character(self, character=None):
    pass
  
  def create_relationship(self, relationship=None):
    pass
  
  def get_people_properties(self):
    engine = _create_engine()
    with engine.connect() as conn:
      self.genders = _get_movie_properties(conn, "GENDER")
      self.ethnicities = _get_movie_properties(conn, "ETHNICITIE")
      self.sexualities = _get_movie_properties(conn, "SEXUALITIE")
      self.roles = _get_movie_properties(conn, "ROLE")
      print(self.ethnicities)




class ImagePanel(tk.Frame):
  def __init__(self, parent, images=None):
    tk.Frame.__init__(self, parent,
      borderwidth=2,
    )
    self.images = images or []
    self.index = 0
    self.savedImages = {}

    self.controlPanel = tk.Frame(self)

    img_label = tk.Label(
      self.controlPanel, text="Image Selector",
      width=10, height=1
    )
    img_label.pack(side="top", pady=5, padx=0)

    #font=('Arial',9,'bold','underline')
    f = Font(img_label, img_label.cget("font"))
    f.configure(underline=True)
    img_label.configure(font=f)

    prev = tk.Button(
      self.controlPanel,
      text="Previous", width=10, height=1,
      command=self.increment_index(-1)
    )
    nextt = tk.Button(
      self.controlPanel,
      text="Next", width=10, height=1,
      command=self.increment_index(1)
    )
    delete = tk.Button(
      self.controlPanel,
      text="Delete", width=10, height=1,
      command=self.delete_image
    )
    
    # prev.pack(side="top")
    # nextt.pack(side="top")
    # delete.pack(side="top")

    self.imageDescriptor = tk.Frame(self.controlPanel)
    self.imageDescriptor.pack(side="top", expand=True, fill="both")

    for widget in [prev, nextt, delete]:#self.controlPanel.winfo_children():
      widget.pack(side="bottom", padx=0, pady=0)

    self.controlPanel.pack(side="left", fill=tk.Y)

    self.imagePanel = tk.Frame(
      self, #bg="white"
      highlightbackground="black", highlightthickness=2
    )
    self.imagePanel.pack(
      side="right", expand=True, fill="both",
      padx=(5, 0), pady=(5, 0)
    )
    
    self.loadImage()

  def saveImagePanel(self):
    if getattr(self, "caption", False):
      self.savedImages[self.images[self.index]] = {
        "caption": self.caption.get("1.0", tk.END)
      }

  def clearImagePanel(self):
    for widgets in self.imagePanel.winfo_children():
        widgets.destroy()
    for widgets in self.imageDescriptor.winfo_children():
        widgets.destroy()
  
  def loadImages(self, images):
    self.images = images
    self.savedImages = {}
    self.index = 0

    self.clearImagePanel()
    self.loadImage()

  def loadImage(self):

    if len(self.images) == 0:
      notify = tk.Label(
        self.imagePanel, text="No Images",

        #height=3, width=10
      )
      notify.pack()
      return

    image1 = Image.open(self.images[self.index])

    panel_height = self.imagePanel.winfo_height()
    width, height = image1.size

    img_size = tk.Label(
      self.imageDescriptor, text=f"({width}, {height})"
    )
    img_size.pack(side="top")

    image1 = image1.resize((int(panel_height/height*width), panel_height), Image.ANTIALIAS)
    next_image = ImageTk.PhotoImage(
      image1
    )

    movieImage = tk.Label(self.imagePanel, image=next_image)
    movieImage.image = next_image

    caption = ""
    if self.images[self.index] in self.savedImages:
      caption = self.savedImages[self.images[self.index]].get("caption", "")

    self.caption = tk.Text(
      self.imagePanel,
      height=3, width=10
    )
    if caption:
      self.caption.insert("1.0", caption)

    movieImage.pack(side="left")
    self.caption.pack(side="right", fill="both", expand=True)

  def delete_image(self):
    #TODO Remove image from dir

    if len(self.images) == 0:
      return

    del self.images[self.index]

    if self.index == len(self.images):
      self.index -= 1

    self.clearImagePanel()
    if len(self.images) > 0:
      self.loadImage()
    else:
      notify = tk.Label(
        self.imagePanel, text="No Images"
      )
      notify.pack(side="right")

  def increment_index(self, increment):
    def func():
      self.saveImagePanel()

      if len(self.images) == 0:
        return

      if increment < 0 and self.index == 0:
        self.index = len(self.images) - 1
      else:
        self.index = (self.index + increment) % len(self.images)
      
      self.clearImagePanel()
      self.loadImage()
    return func

class ChecklistBox(tk.Frame):
  def __init__(self, parent, name, choices, height=100, width=150, **kwargs):
    tk.Frame.__init__(self, parent)

    label = tk.Label(self, text=name)
    label.pack(side="top", fill=tk.X)

    scroll_bar = tk.Scrollbar(self)
    scroll_bar.pack(side=tk.RIGHT, fill = tk.Y)

    # creating a canvas
    canv = tk.Canvas(self)
    canv.config(relief = 'flat', width=width, height=height, bd = 2)
    # placing a canvas into frame
    #self.canv.grid(column = 0, row = 0, sticky = 'nsew')
    canv.pack(side="left", fill=tk.Y)

    subFrame = tk.Frame(self)#relief=tk.GROOVE, bd=1

    self.vars = {}
    bg = self.cget("background")
    for i, choice in choices.iterrows():
      var = tk.IntVar()
      self.vars[choice.ID] = var
      cb = tk.Checkbutton(subFrame, var=var, text=choice.LABEL,
                          onvalue=1, offvalue=0,
                          anchor="w", width=20, background=bg,
                          relief="flat", highlightthickness=0
      )
      cb.pack(side="top", fill="both", anchor="w", expand=True)
    

    #subFrame.pack(side="left", fill="both", expand=True)
    #subFrame.pack_propagate(0)
    canv.create_window(0, 0, window = subFrame, anchor = 'nw')
    parent.update_idletasks() 
    bbox = canv.bbox("all")
    #print(bbox, subFrame.bbox("all"), subFrame.winfo_height() )
    canv.config(
      yscrollcommand = scroll_bar.set,
      scrollregion = (0, 0, width, subFrame.winfo_height()) #bbox#
    )
    scroll_bar.config(command=canv.yview)
    scroll_bar.lift(subFrame) 
    label.lift()

  def getCheckedItems(self):
    ids = []
    for idd, checked  in self.vars.items():
      value =  checked.get()
      if value:
        ids.append(idd)
    return ids

class MovieLoader(tk.Frame):
  def __init__(self, parent, name, choices, height=100, width=150, **kwargs):
    tk.Frame.__init__(self, parent)

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
    #self.root.configure(bg="#f2c7ee")
    self.root.title("Q-Watch Movie Loader")
    #self.root.geometry('500x500')

  def configure_menu(self):
    """ Menu Operations Available."""
    self.menubar = tk.Menu(self.root)
    self.fileMenu = tk.Menu(self.menubar, tearoff=0)
    self.menubar.add_cascade(label='File', menu=self.fileMenu)
    self.fileMenu.add_command(label='Save', command=None)
    self.fileMenu.add_separator()
    self.fileMenu.add_command(label='Exit', command=self.root.destroy)
  
  def save_movie(self):
    pass

  def update_contents(self):
    # if "age" in self.movie_info:
    props = ["age", "summary", "year", "language", "country", "running_time"]
    print("Update_contents: \n", self.movie_info)
    for prop in props:
      if prop in self.movie_info:
        if hasattr(self, prop):
          #getattr(self, prop).delete('0', tk.END)
          getattr(self, prop).insert(tk.END, self.movie_info[prop])
        else:
          print(f"No {prop} console item")
    
    self.load_next_movie_image()

  def load_next_movie_image(self):
    # Load up movie images
    # image1 = Image.open(self.movie_info["images"][0])
    # image1 = image1.resize((100, 100), Image.ANTIALIAS)
    # next_image = ImageTk.PhotoImage(
    #   image1
    # )

    # self.movieImage = tk.Label(self.root, image=next_image)
    # self.movieImage.image = next_image
    # self.movieImage.grid(column=3, row=4, columnspan=2, rowspan=2)

    self.imagePanel.loadImages(self.movie_info["images"])


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

    self.movie_info = {
      **self.movie_info,
      **movie_info,
      **details
    }

    if "url" in self.movie_info:
      #self.url = tk.Label(self.shortFrame, text="Wiki URL")
      fr = tk.Frame(self.root)

      self.url = tk.Button(
        fr,
        text="Wiki URL",
        width=10, height=1,
        command=lambda: webbrowser.open_new(self.movie_info["url"])
      )
      self.url.pack(side="left")
      fr.grid(column=0, columnspan=2, row=7+len(self.shortFrames))
      self.shortFrames.append(fr)

    self.update_contents()

  @staticmethod
  def create_menuList(window, name, items):
    menubutton = tk.Menubutton(
      window,
      text=name,
      relief=tk.RAISED
    )
    menu = tk.Menu(menubutton, tearoff=0)
    #menubutton.configure(menu=menu)
    menubutton["menu"] = menu
    menubutton.configure(menu=menu)
    menubutton.menu = menu

    listItems = {}
    for i, item in items.iterrows():
        var = tk.IntVar()
        menubutton.menu.add_checkbutton(label=item.LABEL, variable=var)
        listItems[item.ID] = var

    return menubutton, listItems

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
  def alert(err_type, mesg):
    if err_type == "warning":
      messagebox.showinfo('Movie Submission Warning', msg)
      messagebox.askyesno("askyesno", "Continue submitting Movie?")
    if err_type == "error":
      messagebox.showerror("showerror", "Movie Entry is Invalid:\n" + error_msg)

  def edit_movie(self):
    """Edit movie selected, load contents from db"""
    #self.movieSelected
    pass



  def __init__(self, movie_info = None):
    if movie_info is None:
      self.movie_info = {}
    else:
      self.movie_info = movie_info

    self.get_movie_properties()
    self.configure_root()
    self.configure_menu()

    self.topFrame = tk.Frame(
      self.root,
      #bg="#f2c7ee",
      #borderwidth=4
    )
    # Movie Title
    self.movie_title_entry = tk.Entry(
      self.topFrame,
      bg="white", fg="black", width=40
    )
    # Searchbar for Movie
    self.search = tk.Button(
      self.topFrame,
      text="Search Movie",
      #height=1, #width=10,
      command=partial(self.get_movie_info, limit=3)
    )
    self.movie_title_entry.pack(side="left", fill="both", expand=True)
    self.search.pack(side="right", padx=(5, 0))#fill="x", expand=False

    #self.
    self.topFrame.grid(row=0, column=0, rowspan=1, columnspan=9, sticky="ew", padx=5)

    ###############################
    # Menu to Edit Existing Movie
    ###############################
    self.movieSelected = tk.StringVar()
    self.movieSelected.set("Select Pre-Existing Movie")
    self.movieSelector = tk.OptionMenu(self.movieSelectorContainer, self.movieSelected, *self.movies.values())
    self.movieSelector.pack(side="left", expand=True, fill=tk.X)
    movieSelectorButton = tk.Button(self.movieSelectorContainer, text="Edit", command=self.edit_movie)
    movieSelectorButton.pack(side="right")

    self.movieSelectorContainer.grid(
      column=2, row=0, rowspan=1, columnspan=4
    )

    # self.trope_label, self.trope_list, self.trope_scroll = self.create_list(self.root, "Tropes", self.tropes)
    # self.represent_label, self.represent_list, self.represent_scroll = self.create_list(self.root, "Represent", self.representations)
    # self.genre_label, self.genre_list, self.genre_scroll = self.create_list(self.root, "Genres", self.genres)

    # self.represent_menuList, self.representationsDict = self.create_menuList(self.root, "Represent", self.representations)

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

    

    #self.shortFrame = tk.Frame(self.root)

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

    # self.ratingLabel = tk.Label(self.shortFrame, text="Rating")
    # self.ratingLabel.pack(side="left", fill="both", expand=True)
    # self.rating = tk.Text(self.shortFrame, height=1, width=2)
    # self.rating.pack(side="left", fill="both", expand=True)
    # self.yearLabel = tk.Label(self.shortFrame, text="Year")
    # self.yearLabel.pack(side="left", fill="both", expand=True)
    # self.year = tk.Text(self.shortFrame, height=1, width=4)
    # self.year.pack(side="left", fill="both", expand=True)
    # self.ageRatingLabel = tk.Label(self.shortFrame, text="Age Rating")
    # self.ageRatingLabel.pack(side="left", fill="both", expand=True)
    # self.ageRating = tk.Text(self.shortFrame, height=1, width=2)
    # self.ageRating.pack(side="left", fill="both", expand=True)


    # Place interactive elements in root
    
    for i, frame in enumerate(self.shortFrames):
      frame.grid(row=7+i, column=0, columnspan=2, rowspan=1, sticky="ew", padx=5)
    

    # self.trope_label.grid(column=5, row=1, columnspan=2)
    # self.trope_list.grid(column=5, row=2, rowspan=2)
    # self.trope_scroll.grid(row=2, column=6, rowspan=2)
    # self.represent_label.grid(column=7, row=1, columnspan=2)
    # self.represent_list.grid(column=7, row=2, rowspan=2)
    # self.represent_scroll.grid(row=2, column=8, rowspan=2)
    # self.genre_label.grid(column=9, row=1, columnspan=2)
    # self.genre_list.grid(column=9, row=2, rowspan=2)
    # self.genre_scroll.grid(row=2, column=10, rowspan=2)

    # self.represent_menuList.grid(column=11, row=2, rowspan=2)

    self.genre_checklist.grid(column=5, row=1, rowspan=2)
    self.trope_checklist.grid(column=6, row=1, rowspan=2)
    self.represent_checklist.grid(column=7, row=1, rowspan=2)
    
    ##############################################################
    # CharacterFrame f

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
  