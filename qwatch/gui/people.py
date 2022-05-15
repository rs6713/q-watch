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

from qwatch.gui.defaults import DEFAULTS
from qwatch.gui.menus import MenuMultiSelector, MenuSingleSelector


logger = logging.getLogger(__name__)


class RelationshipPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, relationships: pd.DataFrame = None, characters: List[Dict] = None):
        """Page to add relationships between characters."""
        ttk.Frame.__init__(self, parent)

        self.relationships = self.process_relationships(
            relationships) if relationships is not None else []
        self.characters = self.process_characters(
            characters) if characters is not None else []

        self.get_relationship_properties()

        ##################################################################
        # Header to Control adding of new relationships
        ##################################################################
        relationshipHeader = ttk.Frame(self)
        relationshipHeader.pack(side="top", padx=5, pady=5, fill=tk.X)

        ttk.Label(relationshipHeader, text="Add Character Relationships").pack(
            side="left", padx=(0, 10))
        ttk.Button(relationshipHeader, text="+", command=lambda: self.add_relationship()).pack(
            side="left", pady=5, padx=5
        )

        relationshipHeader.pack(side="top", padx=5, pady=5, fill=tk.X)
        relationshipContent = ttk.Frame(self)

        self.scrollBar = ttk.Scrollbar(relationshipContent)
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canv = tk.Canvas(relationshipContent)
        self.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.relationshipContainer = ttk.Frame(self.canv)
        self.relationshipContainer.pack(
            side="top", fill=tk.X, expand=True, anchor="nw"
        )

        for relationship in self.relationships:
            self.add_relationship(relationship)

        self.canv.create_window(
            (0, 0), window=self.relationshipContainer, anchor="nw", tags="my_frame"
        )
        self.canv.bind('<Configure>', self.resize_window)
        parent.update_idletasks()
        self.canv.config(
            yscrollcommand=self.scrollBar.set,
            scrollregion=(0, 0, self.relationshipContainer.winfo_width(),
                          self.relationshipContainer.winfo_height())
        )
        self.scrollBar.config(command=self.canv.yview)
        # self.scrollBar.lift(self.relationshipContainer)

        # Scrollwheel handling
        def _on_mousewheel(event):
            self.canv.yview_scroll(int(-1*(event.delta/120)), "units")
        # Configure canv with scroll wheel
        self.bind('<Enter>', lambda _: self.canv.bind_all(
            "<MouseWheel>", _on_mousewheel))
        self.bind('<Leave>', lambda _: self.canv.unbind_all("<MouseWheel>"))

        relationshipContent.pack(
            side="top", fill="both", expand=True, anchor="nw"
        )

    def resize_window(self, event):
        """On resize of canvas, ensure subframe matches width."""
        self.canv.itemconfigure("my_frame", width=event.width)
        self.relationshipContainer.configure(
            width=event.width
        )  # self.canv.winfo_width()

    def process_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Convert relationships to variables for interaction."""
        return [
            {
                "ID": r["ID"],
                "CHARACTER_ID1": tk.IntVar(value=r["CHARACTER_ID1"]),
                "CHARACTER_ID2": tk.IntVar(value=r["CHARACTER_ID2"]),
                "RELATIONSHIP_ID": tk.IntVar(value=r["RELATIONSHIP_ID"]),
                "EXPLICIT": tk.IntVar(value=r["EXPLICIT"])
            }
            for r in relationships
        ]

    def process_characters(self, characters: List[Dict]) -> pd.DataFrame:
        """Transform characters list dict into form intakable by MenuSingleSelector"""
        return pd.DataFrame([
            {"LABEL": c["FIRST_NAME"] + " " + c["LAST_NAME"], "ID": c["ID"]}
            for c in characters
        ])

    def update_contents(self, people):
        if "characters" in people:
            self.characters = self.process_characters(people["characters"])

        self.refresh_ui()

    def delete_relationship(self, idd):
        logger.debug(f"Deleting relationship {idd}")
        self.relationships = [
            r for r in self.relationships if r["ID"] != idd
        ]
        self.refresh_ui()

    def refresh_ui(self):
        for widget in self.relationshipContainer.winfo_children():
            widget.destroy()

        for relationship in self.relationships:
            self.add_relationship(relationship)

    def get_contents(self):
        """ TODO: Get relationships for external db storing."""
        pass

    def add_relationship(self, relationship=None):
        if relationship is None:
            relationship = {
                "ID": uuid.uuid4().int & (1 << 64)-1,
                "CHARACTER_ID1": tk.IntVar(),
                "CHARACTER_ID2": tk.IntVar(),
                "RELATIONSHIP_ID": tk.IntVar(),
                "EXPLICIT": tk.IntVar(1)  # True in the majority of cases
            }
            self.relationships.append(relationship)

        relationshipContainerFrame = ttk.Frame(
            self.relationshipContainer
        )
        relationshipFrame = ttk.Frame(relationshipContainerFrame)

        ####################################################
        # Relationship Statement
        ####################################################
        r_statement = ttk.Frame(relationshipFrame)
        MenuSingleSelector(
            r_statement, "Character 1", self.characters, var=relationship["CHARACTER_ID1"]
        ).pack(side="left")
        ttk.Label(r_statement, text=" is the ").pack(side="left")
        MenuSingleSelector(
            r_statement, "Relationship Type", self.OPTIONS["relationships"], var=relationship["RELATIONSHIP_ID"]
        ).pack(side="left")
        ttk.Label(r_statement, text=" of ").pack(side="left")
        MenuSingleSelector(
            r_statement, "Character 2", self.characters, var=relationship["CHARACTER_ID2"]
        ).pack(side="left")
        r_statement.grid(row=0, column=0, pady=(0, 5), sticky=tk.W)

        ##############################################
        # Relationship Qualifiers
        ##############################################
        e_statement = ttk.Frame(relationshipFrame)
        ttk.Checkbutton(
            e_statement, text="Explicit Relationship?", variable=relationship["EXPLICIT"],
            style='Switch.TCheckbutton'
        ).pack(side="left")
        e_statement.grid(row=1, column=0, padx=5, pady=(0, 5), sticky=tk.W)

        relationshipFrame.pack(side="left")

        ################################################
        # Command Panel
        ################################################
        ttk.Button(
            relationshipContainerFrame, text="Remove", command=partial(self.delete_relationship, relationship["ID"])
        ).pack(side=tk.RIGHT, anchor="ne", padx=(20, 0))

        relationshipContainerFrame.pack(side=tk.TOP, expand=1, fill=tk.X,
                                        padx=(5, 20), anchor="nw")

        # Resize canvas scrollable window
        self.update_idletasks()
        self.canv.config(
            scrollregion=(
                0, 0,
                self.relationshipContainer.winfo_width(),
                self.relationshipContainer.winfo_height()
            )
        )

    def get_relationship_properties(self):
        """ Retrieve relationship mappings from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            relationships = _get_movie_properties(conn, "RELATIONSHIP")

            self.OPTIONS = {
                "relationships": relationships,
            }


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
            self.actors = None

        self.update_people = update_people
        self.is_character = is_character

        self.get_people_properties()

        personHeader = ttk.Frame(self)

        if is_character:
            lbl = "Insert Characters in movie"
        else:
            lbl = "Insert People working on the movie"

        ttk.Label(personHeader, text=lbl).pack(
            side="left", padx=(0, 10))
        ttk.Button(personHeader, text="+", command=lambda: CreatePerson(self.save_person, is_character=self.is_character, options=self.OPTIONS, actors=self.actors)).pack(
            side="left", pady=5, padx=5
        )

        personHeader.pack(side="top", padx=5, pady=5, fill=tk.X)

        self.personContainer = ttk.Frame(self)

        self.personContainer.pack(
            side="top", fill="both", expand=True, anchor="nw"
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

        personFrame = ttk.Frame(self.personContainer)
        # Name
        descriptors = [f"{person['FIRST_NAME']} {person['LAST_NAME']}"]

        if not self.is_character:
            descriptors.append(person["DOB"] or "[DOB UNKNOWN]")
            descriptors.append(self.get_options(person, "ROLES"))
        else:
            descriptors.append(self.get_options(person, 'CAREER'))
            descriptors.append(
                'Main' if person["MAIN"] else 'Side Character')

        lbl = ttk.Label(personFrame, text=" \u2022 ".join(descriptors))
        lbl.config(font=(
            DEFAULTS["FONT_FAMILY"],
            int(DEFAULTS["FONT_SIZE"]),
            "bold"
        ))
        lbl.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="w")

        identities = []
        for identity in ["SEXUALITIES", "GENDERS", "TRANSGENDER", "ETHNICITIES", "DISABILITIES"]:
            identities.append(self.get_options(person, identity))
        if self.is_character:
            identities.append((person["HAIR_COLOR"] or "[HAIR_COLOR UNKNOWN]"))
        ttk.Label(personFrame, text=" \u2022 ".join(identities)).grid(
            row=1, column=0, padx=5, pady=(0, 5), sticky="w"
        )

        if self.is_character:
            if person.get("ACTOR", None) is not None:

                actor = [a for a in self.actors if a["ID"]
                         == person["ACTOR"]][0]
                actor = f"{actor['FIRST_NAME']} {actor['LAST_NAME']}"
            else:
                actor = "[ACTOR UNKNOWN]"

            ttk.Label(personFrame, text=f"Played by: {actor}").grid(
                row=2, column=0, padx=5, pady=(0, 5), sticky="w"
            )

        ttk.Label(personFrame, text=person["BIO"]).grid(
            row=3, column=0, padx=5, pady=5, sticky="w"
        )

        ################################################
        # Command Panel
        ################################################
        ttk.Button(
            personFrame, text="Remove", command=partial(self.delete_person, person["ID"])
        ).grid(column=2, padx=(50, 0), pady=(0, 5), sticky=tk.E, row=0)

        ttk.Button(
            personFrame, text="Edit", command=lambda: CreatePerson(self.save_person, is_character=self.is_character, person=person, options=self.OPTIONS, actors=self.actors)
        ).grid(column=2, padx=(50, 0), sticky=tk.E, row=1)

        personFrame.pack(side=tk.TOP, expand=1, fill=tk.X,
                         padx=(5, 20), anchor="w")

    def update_contents(self, people):
        logger.debug("Updating contents")
        if self.is_character and "people" in people.keys():
            logger.debug(f"There are {len(people['people'])} actors")
            self.actors = [] if people.get(
                "people", None) is None else people["people"]

    def get_options(self, person: Dict, option: str, OPTIONS: pd.DataFrame = None):
        if OPTIONS is None:
            OPTIONS = self.OPTIONS[option]
        if person[option] is None or (isinstance(person[option], list) and len(person[option]) == 0):
            return f'[{option} UNKNOWN]'
        elif isinstance(person[option], list):
            return ", ".join([
                f"{row.LABEL} - {row.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in row.index else row.LABEL
                for _, row in OPTIONS.iterrows()
                if row.ID in person[option]
            ])
        else:
            row = OPTIONS[OPTIONS.ID ==
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

        # Temporary unique identifier, approximate, non-zero risk of collision
        if "ID" not in self.person:
            self.person["ID"] = uuid.uuid4().int & (1 << 64)-1

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
        if self.is_character and len(self.actors):
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
            level2, "Trans Status", self.OPTIONS["TRANSGENDER"], default=self.person.get("TRANSGENDER", None)
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
        self.relationshipPage = RelationshipPage(
            self.notebook, relationships=self.people_overview[
                "relationships"], characters=self.people_overview["characters"]
        )
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
        logger.debug(f"Update People Qualities: {people.keys()}")

        if "people" in people.keys():
            logger.debug("Updating character page contents")
            self.characterPage.update_contents(people)
            # TODO update relationships options

        if "characters" in people.keys():
            # TODO Update relationships/actions options
            logger.debug("Update relationships/actions")
