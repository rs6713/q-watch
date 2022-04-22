import tkinter as tk
from tkinter import ttk

from qwatch.io import _create_engine
from qwatch.io.input import (
  get_representations,
  get_tropes,
  get_genres,
  get_movies_ids,
  _get_movie_properties,
)

from qwatch.gui.menus import MenuMultiSelector

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
    """ Retrieve person traits from db."""
    engine = _create_engine()
    with engine.connect() as conn:
      self.genders = _get_movie_properties(conn, "GENDER")
      self.ethnicities = _get_movie_properties(conn, "ETHNICITIE")
      self.sexualities = _get_movie_properties(conn, "SEXUALITIE")
      self.roles = _get_movie_properties(conn, "ROLE")

