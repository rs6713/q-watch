from functools import partial
import logging
from typing import Callable, Dict, List
import uuid

import pandas as pd
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

from qwatch.gui.menus import MenuMultiSelector, MenuSingleSelector


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class PersonPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, update_people: Callable, is_character: bool = False, people: List[Dict] = None):
        """
        Page to manage people (actors, writer etc) associated with the film.

        Params
        ------
        update_people: to update people list
        """
        ttk.Frame.__init__(self, parent)

        if is_character:
            self.people = [] if people.get(
                "characters", None) is None else people["characters"]
            self.actors = [] if people.get(
                "people", None) is None else people["people"]

            # TODO Get actors only
            # else [
            #       p for p in people["people"]
            #       if "ACTOR" in p["ROLES"]
            #     ]
        else:
            self.people = [] if people.get(
                "people", None) is None else people["people"]

        self.update_people = update_people
        self.is_character = is_character

        self.get_people_properties()

        personHeader = ttk.Frame(self)
        personHeader.pack(side="top", padx=5, pady=5, fill=tk.X)

        if is_character:
            lbl = "Insert Characters in movie"
        else:
            lbl = "Insert People working on the movie"

        ttk.Label(personHeader, text=lbl).pack(
            side="left", padx=(0, 10))
        ttk.Button(personHeader, text="+", command=lambda: CreatePerson(self.save_person, is_character=self.is_character, options=self.OPTIONS)).pack(
            side="left", pady=5, padx=5
        )

        self.personContainer = ttk.Frame(self)

        self.personContainer.pack(
            side="top", fill="both", expand=True
        )

        for person in self.people:
            self.add_person_ui(person)

    def refresh_ui(self):
        for widget in self.personContainer.winfo_children():
            widget.destroy()

        for person in self.people:
            self.add_person_ui(person)

    def delete_person(self, person):
        """ Delete person from list."""
        logger.debug(f"Deleting person in {__class__}: {person}")

        self.people = [
            p for p in self.people if p["ID"] != person["ID"]
        ]

        self.refresh_ui()

        # Update People lists for other people management pages
        prop = "characters" if self.is_character else "people"
        self.update_people({prop: self.people})

    def save_person(self, person):
        logger.debug(f"Saving person in {__class__}: {person}")

        # Pre-existing person, edited
        if person["ID"] in [p["ID"] for p in self.people]:
            self.people = [
                p if p["ID"] != person["ID"] else person for p in self.people
            ]
            self.refresh_ui()
        # New person
        else:
            self.people = [
                *self.people, person
            ]
            # TODO: Update ui
            self.add_person_ui(person)

        # Update People lists for other people management pages
        prop = "characters" if self.is_character else "people"
        self.update_people({prop: self.people})

    def add_person_ui(self, person):
        """Add person to ui"""
        logger.debug(f"Adding person to UI in {__class__}: {person}")
        print(person)
        personFrame = ttk.Frame(self.personContainer)
        # Name
        ttk.Label(personFrame, text=f"{person['FIRST_NAME']} {person['LAST_NAME']}").grid(
            row=0, column=0, padx=5, pady=(0, 2))
        if not self.is_character:
            #
            ttk.Label(personFrame, text=self.get_options(
                person, "ROLES")).grid(row=1, column=0, padx=5, pady=(0, 5))

        ################################################
        # Command Panel
        ################################################
        ttk.Button(
            personFrame, text="Remove", command=partial(self.delete_person, person["ID"])
        ).grid(column=3, padx=(20, 0), sticky=tk.E, row=0)

        ttk.Button(
            personFrame, text="Edit", command=lambda: CreatePerson(self.save_person, is_character=self.is_character, person=person, options=self.OPTIONS)
        ).grid(column=3, padx=(20, 0), sticky=tk.E, row=1)

    def update_contents(self, people):
        if self.is_character and "people" in people:
            self.actors = [] if people.get(
                "people", None) is None else people["people"]

    def get_options(self, person: Dict, option: str):

        if isinstance(person[option], list):
            return ", ".join([
                f"{row.LABEL} - {row.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in row.index else row.LABEL
                for _, row in self.OPTIONS[option].iterrows()
                if row.ID in person[option]
            ])
        else:
            row = self.OPTIONS[option][self.OPTIONS[option].ID ==
                                       person[option]].iloc[0, :]
            return f"{row.LABEL} - {row.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in row.index else row.LABEL

    def get_people_properties(self):
        """ Retrieve person mappings from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            genders = _get_movie_properties(conn, "GENDER")
            ethnicities = _get_movie_properties(conn, "ETHNICITIE")
            sexualities = _get_movie_properties(conn, "SEXUALITIE")
            roles = _get_movie_properties(conn, "ROLE")
            disabilities = _get_movie_properties(conn, "DISABILITIE")
            careers = _get_movie_properties(conn, "CAREER")
            transgenders = _get_movie_properties(conn, "TRANSGENDER")
            self.OPTIONS = {
                "GENDERS": genders,
                "ETHNICITIES": ethnicities,
                "SEXUALITIES": sexualities,
                "ROLES": roles,
                "DISABILITIES": disabilities,
                "CAREER": careers,
                "TRANSGENDER": transgenders,
            }


class CreatePerson(tk.Toplevel):
    def __init__(self, save_action, is_character: bool, person: Dict = None, actors: List[Dict] = None, options: Dict = None):
        tk.Toplevel.__init__(self, pady=5, padx=5)
        self.wm_title(
            f"Create {'Person' if not is_character else 'Character'}")

        self.person = person if person is not None else {}
        self.actors = actors if actors is not None else []
        self.is_character = is_character
        self.save_action = save_action

        if options is None:
            self.get_people_properties()
        else:
            self.OPTIONS = options

        self.create_ui()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def validate_contents(self):
        return True

    def save(self) -> None:
        if not self.validate_contents():
            return

        self.person = {
            **self.person,  # To overwrite, keep unaltered qualities
            "FIRST_NAME": self.first_name.get(),
            "LAST_NAME": self.last_name.get(),
            "BIO": self.bio.get("1.0", tk.END),
            "ETHNICITIES": self.ethnicity_menu.get_selected_options(),
            "SEXUALITIES": self.sexuality_menu.get_selected_option(),
            "DISABILITIES": self.disability_menu.get_selected_options(),
            "GENDERS": self.gender_menu.get_selected_option(),
            "TRANSGENDER": self.transgender_menu.get_selected_option(),
        }
        if self.is_character:
            self.person = {
                **self.person,
                "CAREER": self.career_menu.get_selected_option(),
                "HAIR_COLOR": self.hair_color.get(),
                "MAIN": self.main.get(),
                "ACTOR": self.actor_menu.get_selected_option(),
            }
        else:
            self.person = {
                **self.person,
                "DOB": self.dob.get(),
                "ROLES": self.role_menu.get_selected_options(),
            }

        # Temporary unique identifier
        if "ID" not in self.person:
            self.person["ID"] = str(uuid.uuid4())

        self.save_action(self.person)
        self.destroy()

    def create_ui(self) -> None:
        """ Create UI to create new person."""

        # First name
        ttk.Label(self, text="First Name").grid(
            column=0, row=0, sticky=tk.W)
        self.first_name = ttk.Entry(self, width=30)
        self.first_name.focus()
        self.first_name.grid(column=1, row=0, sticky=tk.W,
                             padx=(0, 10), pady=(0, 5))
        if "FIRST_NAME" in self.person:
            self.first_name.insert(0, self.person["FIRST_NAME"])

        # Last Name
        ttk.Label(self, text="Last Name").grid(
            column=0, row=1, sticky=tk.W)
        self.last_name = ttk.Entry(self, width=30)
        self.last_name.grid(column=1, row=1, sticky=tk.W,
                            padx=(0, 10), pady=(0, 5))
        if "LAST_NAME" in self.person:
            self.last_name.insert(0, self.person["LAST_NAME"])

        # DOB
        if not self.is_character:
            ttk.Label(self, text="Date of Birth").grid(
                column=0, row=2, sticky=tk.W)
            self.dob = ttk.Entry(self, width=30)
            self.dob.grid(column=1, row=2, sticky=tk.W,
                          padx=(0, 10), pady=(0, 5))
            if "DOB" in self.person:
                self.dob.insert(0, self.person["DOB"])
        else:
            ttk.Label(self, text="Hair Color").grid(
                column=0, row=2, sticky=tk.W)
            self.hair_color = ttk.Entry(self, width=30)
            self.hair_color.grid(column=1, row=2, sticky=tk.W,
                                 padx=(0, 10), pady=(0, 5))
            if "HAIR_COLOR" in self.person:
                self.hair_color.insert(0, self.person["HAIR_COLOR"])

        button_frame = ttk.Frame(self)

        self.sexuality_menu = MenuSingleSelector(
            button_frame, "Sexuality", self.OPTIONS["SEXUALITIES"],
            default=self.person.get("SEXUALITIES", None)
        )
        self.sexuality_menu.pack(
            side="left", fill=tk.X, expand=True, padx=(0, 5))

        self.gender_menu = MenuSingleSelector(
            button_frame, "Gender", self.OPTIONS["GENDERS"],
            default=self.person.get("GENDERS", None))
        self.gender_menu.pack(side="left", fill=tk.X, expand=True, padx=(0, 5))

        self.ethnicity_menu = MenuMultiSelector(
            button_frame, "Ethnicity", self.OPTIONS["ETHNICITIES"],
            default=self.person.get("ETHNICITIES", []))
        self.ethnicity_menu.pack(
            side="left", fill=tk.X, expand=True, padx=(0, 5))

        self.disability_menu = MenuMultiSelector(
            button_frame, "Disability", self.OPTIONS["DISABILITIES"],
            default=self.person.get("DISABILITIES", [])
        )
        self.disability_menu.pack(side="left", fill=tk.X, expand=True)

        button_frame.grid(column=0, row=3, pady=(10, 0),
                          rowspan=1, columnspan=4, sticky="ew")

        #########################################################
        # Transgender, Role
        #########################################################
        level2 = ttk.Frame(self)
        if len(self.actors):
            actors = pd.DataFrame([])
            actors.loc[:, "LABEL"] = [
                f'{a["FIRST_NAME"]} {a["LAST_NAME"]}' for a in self.actors]
            actors.loc[:, "ID"] = [a["ID"] for a in self.actors]
            self.actor_menu = MenuSingleSelector(
                level2, "Actor", actors, default=self.person.get("ACTOR", None)
            )
            self.actor_menu.pack(
                side="left", fill=tk.X, expand=True, padx=(0, 5)
            )

        self.transgender_menu = MenuSingleSelector(
            level2, "Transgender", self.OPTIONS["TRANSGENDER"], default=self.person.get("TRANSGENDER", None)
        )
        self.transgender_menu.pack(
            side="left", fill=tk.X, expand=True, padx=(0, 5))

        if not self.is_character:
            self.role_menu = MenuMultiSelector(
                level2, "Roles", self.OPTIONS["ROLES"],
                default=self.person.get("ROLES", []))
            self.role_menu.pack(side="left", fill=tk.X, expand=True)
        else:
            self.career_menu = MenuSingleSelector(
                level2, "Careers", self.OPTIONS["CAREER"], default=self.person.get("CAREER", None)
            )
            self.career_menu.pack(side="left", fill=tk.X, expand=True)

            self.main = tk.IntVar(value=self.person.get("MAIN", 0))
            main_btn = ttk.Checkbutton(
                level2, text="Main Character", variable=self.main,
                style='Switch.TCheckbutton'
            )
            main_btn.pack(
                side="left", fill=tk.X, expand=True, padx=(0, 5))

        level2.grid(column=0, row=4, pady=(5, 0),
                    rowspan=1, columnspan=4, sticky="ew")

        self.bio = tk.Text(
            self, height=3, width=5
        )
        self.bio.grid(row=5, pady=(5, 0), column=0, columnspan=4, sticky="ew")

        ###################################################
        # Control Panel
        ###################################################
        save_button = ttk.Button(
            self, text="Save", width=10, command=self.save, style='Accent.TButton')
        save_button.grid(column=3, padx=(20, 0), sticky=tk.E, row=0)

        exit_button = ttk.Button(
            self, text="Cancel", width=10, command=lambda: self.destroy())
        exit_button.grid(column=3, padx=(20, 0), sticky=tk.E, row=1)

    def get_people_properties(self):
        """ Retrieve person traits from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            genders = _get_movie_properties(conn, "GENDER")
            ethnicities = _get_movie_properties(conn, "ETHNICITIE")
            sexualities = _get_movie_properties(conn, "SEXUALITIE")
            roles = _get_movie_properties(conn, "ROLE")
            disabilities = _get_movie_properties(conn, "DISABILITIE")
            careers = _get_movie_properties(conn, "CAREER")
            transgenders = _get_movie_properties(conn, "TRANSGENDER")
            self.OPTIONS = {
                "GENDERS": genders,
                "ETHNICITIES": ethnicities,
                "SEXUALITIES": sexualities,
                "ROLES": roles,
                "DISABILITIES": disabilities,
                "CAREER": careers,
                "TRANSGENDER": transgenders,
            }


class PeopleManagementPanel(ttk.Frame):
    def __init__(self, parent, people_overview=None):
        tk.Frame.__init__(self, parent)

        self.people_overview = {
            "characters": [],
            "people": [],
            "relationships": [],
            "actions": []
        } if people_overview is None else people_overview

        self.notebook = ttk.Notebook(self, height=300)
        self.personPage = PersonPage(
            self.notebook, self.update_people_overview, is_character=False, people=self.people_overview)
        self.characterPage = PersonPage(
            self.notebook, self.update_people_overview, is_character=True, people=self.people_overview)

        # TODO: Own classes
        self.relationshipPage = ttk.Frame(self.notebook)
        self.actionPage = ttk.Frame(self.notebook)

        self.notebook.add(self.personPage, text="Personnel")
        self.notebook.add(self.characterPage, text="Characters")
        self.notebook.add(self.relationshipPage, text="Relationships")
        self.notebook.add(self.actionPage, text="Actions")

        self.notebook.pack(expand=1, fill="both")

    def get_items(self) -> None:
        """ Get all characters/people/actions/relationships in movie self.people_overview."""
        pass

    def update_people_overview(self, people: Dict) -> None:
        """
        Called to subpages, to update their contents with new people.
        Depending on which properties have been updated.
        """
        if "people" in people:
            self.characterPage.update_contents(people)
            # TODO update relationships options

        if "characters" in people:
            # TODO Update relationships/actions options
            logger.debug("Update relationships/actions")
