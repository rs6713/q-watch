from functools import partial
import logging
from typing import Callable, Dict, List, Optional, Union
import uuid

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from qwatch.io import _create_engine
from qwatch.io.input import (
    get_representations,
    get_tropes,
    get_genres,
    get_movies_ids,
    _get_movie_labels,
    get_id,
    get_actors,
)

from qwatch.gui.defaults import DEFAULTS
from qwatch.gui.menus import MenuMultiSelector, MenuSingleSelector


logger = logging.getLogger(__name__)


class ActionsPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, character_actions: pd.DataFrame = None, characters: pd.DataFrame = None) -> None:
        """Page to add relationships between characters."""
        ttk.Frame.__init__(self, parent)

        self.character_actions = self.process_character_actions(
            character_actions) if character_actions is not None else []
        self.characters = self.process_characters(
            characters) if characters is not None else []

        self.get_action_properties()

        ##################################################################
        # Header to Control adding of new relationships
        ##################################################################
        actionsHeader = ttk.Frame(self)
        actionsHeader.pack(side="top", padx=5, pady=5, fill=tk.X)

        ttk.Label(actionsHeader, text="Add Character Actions").pack(
            side="left", padx=(0, 10))
        ttk.Button(actionsHeader, text="+", command=self.add_character_action).pack(
            side="left", pady=5, padx=5
        )

        actionsHeader.pack(side="top", padx=5, pady=5, fill=tk.X)
        actionsContent = ttk.Frame(self)

        self.scrollBar = ttk.Scrollbar(actionsContent)
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canv = tk.Canvas(actionsContent)
        self.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.actionsContainer = ttk.Frame(self.canv)
        self.actionsContainer.pack(
            side="top", fill=tk.X, expand=True, anchor="nw"
        )

        for character_action in self.character_actions:
            self.add_character_action(character_action)

        self.canv.create_window(
            (0, 0), window=self.actionsContainer, anchor="nw", tags="my_frame"
        )
        self.canv.bind('<Configure>', self.resize_window)
        parent.update_idletasks()
        self.canv.config(
            yscrollcommand=self.scrollBar.set,
            scrollregion=(0, 0, self.actionsContainer.winfo_width(),
                          self.actionsContainer.winfo_height())
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

        actionsContent.pack(
            side="top", fill="both", expand=True, anchor="nw"
        )

    def load(self, characters: pd.DataFrame = None, character_actions: pd.DataFrame = None):
        self.character_actions = self.process_character_actions(
            character_actions) if character_actions is not None else []
        self.characters = self.process_characters(
            characters) if characters is not None else []

        self.refresh_ui()

    def resize_window(self, event) -> None:
        """On resize of canvas, ensure subframe matches width."""
        self.canv.itemconfigure("my_frame", width=event.width)
        self.actionsContainer.configure(
            width=event.width
        )  # self.canv.winfo_width()

    def process_character_actions(self, character_actions: pd.DataFrame) -> List[Dict]:
        """Convert character_actions to variables for interaction."""
        return [
            {
                "CHARACTER_ID": tk.IntVar(value=ca["CHARACTER_ID"]),
                "ACTION_ID": ca["ACTION_ID"],
            }
            for ca in character_actions.to_dict("records")
        ]

    def process_characters(self, characters: pd.DataFrame) -> pd.DataFrame:
        """Transform characters list dict into form intakable by MenuSingleSelector"""
        return pd.DataFrame([
            {"LABEL": c["FIRST_NAME"] + " " + c["LAST_NAME"], "ID": c["ID"]}
            for c in characters.to_dict("records")
        ], columns=["LABEL", "ID"])

    def update_contents(self, characters: pd.DataFrame = None) -> None:
        if characters is not None:
            logger.debug(
                f"Updating contents in {__class__} with characters: {characters}")
            self.characters = self.process_characters(characters)

            # Only keep character actions associated with existing characters
            self.character_actions = [
                r for r in self.character_actions
                if r["CHARACTER_ID"].get() in self.characters["ID"].values
            ]

        self.refresh_ui()

    def delete_character_action(self, action_id: int) -> None:
        logger.debug(f"Deleting character action {action_id}")
        self.character_actions = [
            ca for ca in self.character_actions if ca["CHARACTER_ID"] != action_id
        ]
        self.refresh_ui()

    def refresh_ui(self) -> None:
        for widget in self.actionsContainer.winfo_children():
            widget.destroy()

        for character_action in self.character_actions:
            self.add_character_action(character_action)

    def get_contents(self) -> pd.DataFrame:
        """ Get character actions for external db storing."""
        character_actions = pd.DataFrame([
            {
                "CHARACTER_ID": ca["CHARACTER_ID"].get(),
                "ACTION_ID": ca["ACTIONS_MENU"].get_selected_options(),
            }
            for ca in self.character_actions
            if len(ca["ACTIONS_MENU"].get_selected_options())
        ])
        logger.debug("Character Actions: %s", character_actions)

        return character_actions

    def add_character_action(self, character_action: Dict = None) -> None:
        if character_action is None:
            character_action = {
                "CHARACTER_ID": tk.IntVar(),
                "ACTION_ID": []
            }
            self.character_actions.append(character_action)

        actionsContainerFrame = ttk.Frame(
            self.actionsContainer
        )
        actionsFrame = ttk.Frame(actionsContainerFrame)

        ####################################################
        # Actions Statement
        ####################################################
        a_statement = ttk.Frame(actionsFrame)
        MenuSingleSelector(
            a_statement, "Character", self.characters, var=character_action["CHARACTER_ID"]
        ).pack(side="left")
        ttk.Label(a_statement, text=" does ").pack(side="left")
        descrip = tk.StringVar(value="")
        actions = MenuMultiSelector(
            a_statement, "Actions", self.OPTIONS["actions"], default=character_action["ACTION_ID"], descrip_var=descrip
        )
        actions.pack(side="left")
        ttk.Label(a_statement, textvariable=descrip).pack(side="left")
        a_statement.grid(row=0, column=0, pady=(0, 5), sticky=tk.W)

        actionsFrame.pack(side="left")

        character_action["ACTIONS_MENU"] = actions

        ################################################
        # Command Panel
        ################################################
        ttk.Button(
            actionsContainerFrame, text="Remove", command=partial(self.delete_character_action, character_action["CHARACTER_ID"])
        ).pack(side=tk.RIGHT, anchor="ne", padx=(20, 0))

        actionsContainerFrame.pack(side=tk.TOP, expand=1, fill=tk.X,
                                   padx=(5, 20), anchor="nw")

        # Resize canvas scrollable window
        self.update_idletasks()
        self.canv.config(
            scrollregion=(
                0, 0,
                self.actionsContainer.winfo_width(),
                self.actionsContainer.winfo_height()
            )
        )

    def get_action_properties(self) -> None:
        """ Retrieve action mappings from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            actions = _get_movie_labels(conn, "ACTION")

            self.OPTIONS = {
                "actions": actions,
            }


class RelationshipPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, relationships: pd.DataFrame = None, characters: pd.DataFrame = None) -> None:
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

    def load(self, characters: pd.DataFrame = None, relationships: pd.DataFrame = None) -> None:
        self.relationships = self.process_relationships(
            relationships) if relationships is not None else []
        self.characters = self.process_characters(
            characters) if characters is not None else pd.DataFrame([])
        self.refresh_ui()

    def resize_window(self, event) -> None:
        """On resize of canvas, ensure subframe matches width."""
        self.canv.itemconfigure("my_frame", width=event.width)
        self.relationshipContainer.configure(
            width=event.width
        )  # self.canv.winfo_width()

    def process_relationships(self, relationships: pd.DataFrame) -> List[Dict]:
        """Convert relationships to variables for interaction."""
        return [
            {
                "ID": r["ID"],
                "CHARACTER_ID1": tk.IntVar(value=r["CHARACTER_ID1"]),
                "CHARACTER_ID2": tk.IntVar(value=r["CHARACTER_ID2"]),
                "RELATIONSHIP_ID": tk.IntVar(value=r["RELATIONSHIP_ID"]),
                "EXPLICIT": tk.IntVar(value=r["EXPLICIT"])
            }
            for r in relationships.to_dict("records")
        ]

    def process_characters(self, characters: pd.DataFrame) -> pd.DataFrame:
        """Transform characters list dict into form intakable by MenuSingleSelector"""
        return pd.DataFrame([
            {"LABEL": c["FIRST_NAME"] + " " + c["LAST_NAME"], "ID": c["ID"]}
            for c in characters.to_dict("records")
        ], columns=["LABEL", "ID"])

    def update_contents(self, characters: pd.DataFrame = None) -> pd.DataFrame:
        if characters is not None:
            self.characters = self.process_characters(characters)

            self.relationships = [
                r for r in self.relationships
                if r["CHARACTER_ID1"].get() in self.characters.ID.values and r["CHARACTER_ID2"].get() in self.characters.ID.values
            ]

        self.refresh_ui()

    def delete_relationship(self, relationship_id: int) -> None:
        logger.debug(f"Deleting relationship {relationship_id}")
        self.relationships = [
            r for r in self.relationships if r["ID"] != relationship_id
        ]
        self.refresh_ui()

    def refresh_ui(self) -> None:
        for widget in self.relationshipContainer.winfo_children():
            widget.destroy()

        for relationship in self.relationships:
            self.add_relationship(relationship)

    def get_contents(self) -> None:
        """ TODO: Get relationships for external db storing."""
        relationships = pd.DataFrame([
            {
                "CHARACTER_ID1": r["CHARACTER_ID1"].get(),
                "CHARACTER_ID2": r["CHARACTER_ID2"].get(),
                "RELATIONSHIP_ID": r["RELATIONSHIP_ID"].get(),
                "EXPLICIT": r["EXPLICIT"].get(),
                "ID": r["ID"]
            }
            for r in self.relationships
            if r["CHARACTER_ID1"].get() > 0 and r["CHARACTER_ID2"].get() > 0 and r["RELATIONSHIP_ID"].get() != 0
        ])
        logger.debug("Character Relationships: %s", relationships)

        return relationships

    def add_relationship(self, relationship: Dict = None) -> None:
        if relationship is None:
            # New relationship needs generated id
            relationship = {
                "ID": uuid.uuid4().int & (1 << 64)-1,
                "CHARACTER_ID1": tk.IntVar(),
                "CHARACTER_ID2": tk.IntVar(),
                "RELATIONSHIP_ID": tk.IntVar(),
                "EXPLICIT": tk.IntVar(value=1)  # True in the majority of cases
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

    def get_relationship_properties(self) -> None:
        """ Retrieve relationship mappings from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            relationships = _get_movie_labels(conn, "RELATIONSHIP")

            self.OPTIONS = {
                "relationships": relationships,
            }


class PersonPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, update_people: Callable, is_character: bool = False, people: pd.DataFrame = None, characters: pd.DataFrame = None) -> None:
        """
        Page to manage people (actors, writer etc) associated with the film.

        Params
        ------
        update_people: to update people list
        """
        ttk.Frame.__init__(self, parent)

        self.get_people_properties()

        if is_character:
            self.people = [] if characters is None else characters.to_dict(
                "records")
            self.actors = [] if people is None else [
                a
                for a in people.to_dict("records")
                if self.actor_id in a.get("ROLE", [])
            ]

        else:
            self.people = [] if people is None else people.to_dict("records")
            self.actors = None

        self.update_people = update_people
        self.is_character = is_character

        personHeader = ttk.Frame(self)

        if is_character:
            lbl = "Insert Characters in movie"
        else:
            lbl = "Insert People working on the movie"

        ttk.Label(personHeader, text=lbl).pack(
            side="left", padx=(0, 10))
        ttk.Button(personHeader, text="+ New", command=lambda: CreatePerson(self.save_person, is_character=self.is_character, options=self.OPTIONS, actors=self.actors)).pack(
            side="left", pady=5, padx=5
        )
        if not self.is_character:
            ttk.Button(personHeader, text="+ Existing",
                       command=lambda: AddPerson(self.save_person)).pack(side="left", pady=5)

        personHeader.pack(side="top", padx=5, pady=5, fill=tk.X)

        self.personContainer = ttk.Frame(self)

        self.personContainer.pack(
            side="top", fill="both", expand=True, anchor="nw"
        )

        personContent = ttk.Frame(self)

        self.scrollBar = ttk.Scrollbar(personContent)
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canv = tk.Canvas(personContent)
        self.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.personContainer = ttk.Frame(self.canv)
        self.personContainer.pack(
            side="top", fill=tk.X, expand=True, anchor="nw"
        )

        for person in self.people:
            self.add_person_ui(person)

        self.canv.create_window(
            (0, 0), window=self.personContainer, anchor="nw", tags="my_frame"
        )
        self.canv.bind('<Configure>', self.resize_window)
        parent.update_idletasks()
        self.canv.config(
            yscrollcommand=self.scrollBar.set,
            scrollregion=(0, 0, self.personContainer.winfo_width(),
                          self.personContainer.winfo_height())
        )
        self.scrollBar.config(command=self.canv.yview)

        # Scrollwheel handling
        def _on_mousewheel(event):
            self.canv.yview_scroll(int(-1*(event.delta/120)), "units")
        # Configure canv with scroll wheel
        self.bind('<Enter>', lambda _: self.canv.bind_all(
            "<MouseWheel>", _on_mousewheel))
        self.bind('<Leave>', lambda _: self.canv.unbind_all("<MouseWheel>"))

        personContent.pack(
            side="top", fill="both", expand=True, anchor="nw"
        )

    def get_contents(self) -> Optional[pd.DataFrame]:
        """ Get people for external db storing."""
        if self.people is None:
            return None

        if self.is_character:
            default_character = {
                "DISABILITY": [],
                "ETHNICITY": [],
                "GENDER": None,
                "MAIN": None,
                "SEXUALITY": None,
                "TRANSGENDER": None,
                "HAIR_COLOR": "",
                "CAREER": None,
                "BIO": ""
            }
            characters = pd.DataFrame([
                {**default_character, **character}
                for character in self.people
            ])
            characters = characters.fillna(np.nan).replace([np.nan], [None])
            logger.debug("Characters: %s", characters)

            return characters
        else:
            default_person = {
                "DISABILITY": [],
                "ETHNICITY": [],
                "GENDER": None,
                "DOB": "",
                "SEXUALITY": None,
                "BIO": "",
                "TRANSGENDER": None,
                "NATIONALITY": "",
            }
            people = pd.DataFrame(
                [{**default_person, **person} for person in self.people]
            )
            people = people.fillna(np.nan).replace([np.nan], [None])
            logger.debug("People: %s", people)
            return people

    def resize_window(self, event) -> None:
        """On resize of canvas, ensure subframe matches width."""
        self.canv.itemconfigure("my_frame", width=event.width)
        self.personContainer.configure(
            width=event.width
        )

    def load(self, people: pd.DataFrame = None, characters: pd.DataFrame = None) -> None:
        if self.is_character:
            self.people = [] if characters is None else characters.to_dict(
                "records")
            self.actors = [] if people is None else [
                a
                for a in people.to_dict("records")
                if self.actor_id in a.get("ROLE", [])
            ]

        else:
            self.people = [] if people is None else people.to_dict("records")
            logger.info(
                "Loading people:%s",
                ', '.join([
                    f'{p["FIRST_NAME"]} {p["LAST_NAME"]}' for p in self.people
                ])
            )
            self.actors = None
        self.refresh_ui()

    def refresh_ui(self) -> None:
        for widget in self.personContainer.winfo_children():
            widget.destroy()

        for person in self.people:
            self.add_person_ui(person)

    def delete_person(self, person_id: int) -> None:
        """ Delete person from list."""
        logger.debug(f"Deleting person in {__class__}: {person_id}")

        self.people = [
            p for p in self.people if p["ID"] != person_id
        ]

        self.refresh_ui()

        # Update People lists for other people management pages
        prop = "characters" if self.is_character else "people"
        if not self.is_character:
            logger.debug("%s Delete post update: \n%s",
                         prop, pd.DataFrame(self.people))

        self.update_people(**{prop: pd.DataFrame(self.people)})

    def save_person(self, person: Dict) -> None:
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
        self.update_people(**{prop: pd.DataFrame(self.people)})

    def add_person_ui(self, person: Dict) -> None:
        """Add person to ui"""
        logger.debug(f"Adding person to UI in {__class__}: {person}")

        person = {
            k: v for k, v in person.items()
            if v is not None and not (isinstance(v, float) and np.isnan(v))
        }
        logger.debug(
            f"Adding person to UI in {__class__} post nan filter: {person}")

        personFrame = ttk.Frame(self.personContainer)

        # Create descriptors sentence for person
        # Name, DOB, ROLE, CAREER, Main Character?
        descriptors = [
            f"{person.get('FIRST_NAME', '[FIRST NAME UNKNOWN]')} {person.get('LAST_NAME', '[LAST_NAME UNKNOWN]')}"]

        if not self.is_character:
            descriptors.append(person.get("DOB", "") or "[DOB UNKNOWN]")
            descriptors.append(self.get_options(person, "ROLE"))

            descriptors.append(
                person.get("NATIONALITY", "") or "[NATIONALITY UNKNOWN]"
            )
        else:
            descriptors.append(self.get_options(person, 'CAREER'))

            if person.get("MAIN", None) is not None:
                descriptors.append(
                    'Main' if person["MAIN"] else 'Side Character'
                )
            else:
                descriptors.append("[MAIN UNKNOWN]")

        logger.debug(descriptors)

        lbl = ttk.Label(personFrame, text=" \u2022 ".join(descriptors))
        lbl.config(font=(
            DEFAULTS["FONT_FAMILY"],
            int(DEFAULTS["FONT_SIZE"]),
            "bold"
        ))
        lbl.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="w")

        # Create . separated list of identities for person/character
        identities = []
        for identity in ["SEXUALITY", "GENDER", "TRANSGENDER", "ETHNICITY", "DISABILITY"]:
            identities.append(self.get_options(person, identity))
        if self.is_character:
            identities.append((person.get("HAIR_COLOR", "")
                              or "[HAIR_COLOR UNKNOWN]"))
        ttk.Label(personFrame, text=" \u2022 ".join(identities)).grid(
            row=1, column=0, padx=5, pady=(0, 5), sticky="w"
        )
        # If character, display actor they are portrayed by
        if self.is_character:
            if person.get("ACTOR_ID", None) is not None and person['ACTOR_ID'] in [a['ID'] for a in self.actors]:

                actor = [a for a in self.actors if a["ID"]
                         == person["ACTOR_ID"]][0]
                actor = f"{actor['FIRST_NAME']} {actor['LAST_NAME']}"
            else:
                actor = "[ACTOR UNKNOWN]"

            ttk.Label(personFrame, text=f"Played by: {actor}").grid(
                row=2, column=0, padx=5, pady=(0, 5), sticky="w"
            )

        # # Character / Actor BIO
        # ttk.Label(personFrame, text=person.get("BIO", "")).grid(
        #     row=3, column=0, padx=5, pady=5, sticky="w"
        # )

        ################################################
        # Command Panel - Edit/Remove Person/Character
        ################################################
        ttk.Button(
            personFrame, text="Remove", command=partial(self.delete_person, person["ID"])
        ).grid(column=2, padx=(50, 0), pady=(0, 5), sticky=tk.E, row=0)

        ttk.Button(
            personFrame, text="Edit", command=lambda: CreatePerson(self.save_person, is_character=self.is_character, person=person, options=self.OPTIONS, actors=self.actors)
        ).grid(column=2, padx=(50, 0), sticky=tk.E, row=1)

        personFrame.pack(side=tk.TOP, expand=1, fill=tk.X,
                         padx=(5, 20), anchor="w")

        # Resize canvas scrollable window
        self.update_idletasks()
        self.canv.config(
            scrollregion=(
                0, 0,
                self.personContainer.winfo_width(),
                self.personContainer.winfo_height()
            )
        )

    def update_contents(self, people: pd.DataFrame = None, characters: pd.DataFrame = None) -> None:
        logger.debug(f"Updating contents in {__class__}")
        if self.is_character and people is not None:
            logger.debug(f"There are {len(people.to_dict('records'))} actors")
            self.actors = people.to_dict("records")
            # Remove characters, whose actors do not exist anymore
            self.people = [
                person if person["ACTOR_ID"] in [a["ID"] for a in self.actors]
                else {**person, "ACTOR_ID": None}
                for person in self.people
            ]
            self.refresh_ui()

    def get_options(self, person: Dict, option: str, OPTIONS: pd.DataFrame = None) -> str:
        # Get Options from
        if OPTIONS is None:
            OPTIONS = self.OPTIONS[option]

        # Person Characteristic is unspecified
        if option not in person or person[option] is None or (isinstance(person[option], list) and len(person[option]) == 0):
            return f'[{option} UNKNOWN]'
        # Person characteristic is an id list
        elif isinstance(person[option], list):
            return ", ".join([
                f"{row.LABEL} - {row.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in row.index else row.LABEL
                for _, row in OPTIONS.iterrows()
                if row.ID in person[option]
            ])
        # Person characteristic is an id
        else:
            row = OPTIONS[OPTIONS.ID == person[option]].iloc[0, :]
            return f"{row.LABEL} - {row.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in row.index else row.LABEL

    def get_people_properties(self) -> None:
        """ Retrieve person mappings from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            genders = _get_movie_labels(conn, "GENDER")
            ethnicities = _get_movie_labels(conn, "ETHNICITIE")
            sexualities = _get_movie_labels(conn, "SEXUALITIE")
            roles = _get_movie_labels(conn, "ROLE")
            disabilities = _get_movie_labels(conn, "DISABILITIE")
            careers = _get_movie_labels(conn, "CAREER")
            transgenders = _get_movie_labels(conn, "TRANSGENDER")
            self.OPTIONS = {
                "GENDER": genders,
                "ETHNICITY": ethnicities,
                "SEXUALITY": sexualities,
                "ROLE": roles,
                "DISABILITY": disabilities,
                "CAREER": careers,
                "TRANSGENDER": transgenders,
            }

            self.actor_id = get_id(conn, "ROLES", "Actor")


class AddPerson(tk.Toplevel):
    def __init__(self, save_action: Callable) -> None:
        tk.Toplevel.__init__(self, pady=5, padx=5)
        self.wm_title(
            "Add Existing Actor"
        )

        engine = _create_engine()
        with engine.connect() as conn:
            actors = get_actors(conn)

        actor_options = [
            f"{actor['FIRST_NAME']} {actor['LAST_NAME']}"
            for actor in actors.to_dict("records")
        ]

        actor_selected = tk.StringVar()
        actor_selected.set("Select Actor")
        actor_selector = tk.OptionMenu(
            self, actor_selected, *actor_options
        )
        actor_selector.config(width=30)
        actor_selector.pack(side="left", padx=(0, 5), fill=tk.X, expand=True)

        def select_actor():
            """ On click, load this movie."""
            selected_actor = [
                actor
                for actor in actors.to_dict("records")
                if f"{actor['FIRST_NAME']} {actor['LAST_NAME']}" == actor_selected.get()
            ]
            if len(selected_actor):
                save_action(selected_actor[0])
                self.destroy()

        # Button to click to open movie selected from option menu
        actor_selector_button = ttk.Button(
            self,
            text="Open",
            command=select_actor,
            style='Accent.TButton'
        )
        actor_selector_button.pack(side="right")


class CreatePerson(tk.Toplevel):
    """ UI to create/edit Character/Person. Then save using external func save_action"""

    def __init__(self, save_action: Callable, is_character: bool, person: Dict = None, actors: List[Dict] = None, options: Dict = None) -> None:
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

    def validate_contents(self) -> bool:
        """TODO: Validate entry for person/character qualities."""
        return True

    def save(self) -> None:
        if not self.validate_contents():
            messagebox.showerror(
                "showerror",
                f"Could not save {'person' if not self.is_character else 'character'} due to invalid data entry."
            )
            return

        self.person = {
            **self.person,  # To overwrite, keep unaltered qualities
            "FIRST_NAME": self.first_name.get(),
            "LAST_NAME": self.last_name.get(),
            "BIO": self.bio.get("1.0", tk.END),
            "ETHNICITY": self.ethnicity_menu.get_selected_options(),
            "SEXUALITY": self.sexuality_menu.get_selected_option(),
            "DISABILITY": self.disability_menu.get_selected_options(),
            "GENDER": self.gender_menu.get_selected_option(),
            "TRANSGENDER": self.transgender_menu.get_selected_option(),
        }
        if self.is_character:
            self.person = {
                **self.person,
                "CAREER": self.career_menu.get_selected_option(),
                "HAIR_COLOR": self.hair_color.get(),
                "MAIN": self.main.get(),
                "ACTOR_ID": self.actor_menu.get_selected_option() if hasattr(self, "actor_menu") else None,
            }
        else:
            self.person = {
                **self.person,
                "DOB": self.dob.get(),
                "ROLE": self.role_menu.get_selected_options(),
                "NATIONALITY": self.nationality.get(),
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

            ttk.Label(self, text="Nationality").grid(
                column=0, row=3, sticky=tk.W)
            self.nationality = ttk.Entry(
                self, width=30
            )
            self.nationality.grid(column=1, row=3, sticky=tk.W,
                                  padx=(0, 10), pady=(0, 5))
            if "NATIONALITY" in self.person:
                self.dob.insert(0, self.person["NATIONALITY"])

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
            button_frame, "Sexuality", self.OPTIONS["SEXUALITY"],
            default=self.person.get("SEXUALITY", 9)
        )
        self.sexuality_menu.pack(
            side="left", fill=tk.X, expand=True, padx=(0, 5))

        self.gender_menu = MenuSingleSelector(
            button_frame, "Gender", self.OPTIONS["GENDER"],
            default=self.person.get("GENDER", 6))
        self.gender_menu.pack(side="left", fill=tk.X, expand=True, padx=(0, 5))

        self.ethnicity_menu = MenuMultiSelector(
            button_frame, "Ethnicity", self.OPTIONS["ETHNICITY"],
            default=self.person.get("ETHNICITY", []))
        self.ethnicity_menu.pack(
            side="left", fill=tk.X, expand=True, padx=(0, 5))

        self.disability_menu = MenuMultiSelector(
            button_frame, "Disability", self.OPTIONS["DISABILITY"],
            default=self.person.get("DISABILITY", [])
        )
        self.disability_menu.pack(side="left", fill=tk.X, expand=True)
        offset = int(not self.is_character)
        button_frame.grid(column=0, row=3 + offset, pady=(10, 0),
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
                level2, "Actor", actors, default=self.person.get("ACTOR_ID", None)
            )
            self.actor_menu.pack(
                side="left", fill=tk.X, expand=True, padx=(0, 5)
            )

        self.transgender_menu = MenuSingleSelector(
            level2, "Trans Status", self.OPTIONS["TRANSGENDER"], default=self.person.get("TRANSGENDER", 1)
        )
        self.transgender_menu.pack(
            side="left", fill=tk.X, expand=True, padx=(0, 5))

        if not self.is_character:
            self.role_menu = MenuMultiSelector(
                level2, "Roles", self.OPTIONS["ROLE"],
                default=self.person.get("ROLE", []))
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

        level2.grid(column=0, row=4 + offset, pady=(5, 0),
                    rowspan=1, columnspan=4, sticky="ew")

        self.bio = tk.Text(
            self, height=3, width=5
        )
        self.bio.grid(row=5 + offset, pady=(5, 0),
                      column=0, columnspan=4, sticky="ew")

        if "BIO" in self.person:
            self.bio.insert(tk.END, self.person["BIO"])

        ###################################################
        # Control Panel
        ###################################################
        save_button = ttk.Button(
            self, text="Save", width=10, command=self.save, style='Accent.TButton')
        save_button.grid(column=3, padx=(20, 0), sticky=tk.E, row=0)

        exit_button = ttk.Button(
            self, text="Cancel", width=10, command=lambda: self.destroy())
        exit_button.grid(column=3, padx=(20, 0), sticky=tk.E, row=1)

    def get_people_properties(self) -> None:
        """ Retrieve person traits from db."""
        engine = _create_engine()
        with engine.connect() as conn:
            genders = _get_movie_labels(conn, "GENDER")
            ethnicities = _get_movie_labels(conn, "ETHNICITIE")
            sexualities = _get_movie_labels(conn, "SEXUALITIE")
            roles = _get_movie_labels(conn, "ROLE")
            disabilities = _get_movie_labels(conn, "DISABILITIE")
            careers = _get_movie_labels(conn, "CAREER")
            transgenders = _get_movie_labels(conn, "TRANSGENDER")
            self.OPTIONS = {
                "GENDER": genders,
                "ETHNICITY": ethnicities,
                "SEXUALITY": sexualities,
                "ROLE": roles,
                "DISABILITY": disabilities,
                "CAREER": careers,
                "TRANSGENDER": transgenders,
            }


class PeopleManagementPanel(ttk.Frame):
    def __init__(self, parent, people: pd.DataFrame = None, characters: pd.DataFrame = None, character_actions: pd.DataFrame = None, relationships: pd.DataFrame = None, update_external: Callable = None) -> None:
        ttk.Frame.__init__(self, parent)

        self.update_external = update_external

        self.notebook = ttk.Notebook(self, height=200)
        self.personPage = PersonPage(
            self.notebook, self.update_people_overview, is_character=False, people=people)
        self.characterPage = PersonPage(
            self.notebook, self.update_people_overview, is_character=True, people=people, characters=characters)

        # TODO: Own classes
        self.relationshipPage = RelationshipPage(
            self.notebook, relationships=relationships, characters=characters
        )
        self.actionPage = ActionsPage(
            self.notebook, characters=characters,
            character_actions=character_actions
        )

        self.notebook.add(self.personPage, text="Personnel")
        self.notebook.add(self.characterPage, text="Characters")
        self.notebook.add(self.relationshipPage, text="Relationships")
        self.notebook.add(self.actionPage, text="Actions")

        self.notebook.pack(expand=1, fill="both")

    def get_items(self) -> Dict:
        """ Get all characters/people/actions/relationships in movie self.people_overview."""
        return {
            "CHARACTERS": self.characterPage.get_contents().to_dict("records"),
            "PEOPLE": self.personPage.get_contents().to_dict("records"),
            "RELATIONSHIPS": self.relationshipPage.get_contents().to_dict("records"),
            "CHARACTER_ACTIONS": self.actionPage.get_contents().to_dict("records")
        }

    def update_people_overview(
            self, people: pd.DataFrame = None, characters: pd.DataFrame = None) -> None:
        """
        Called to subpages, to update their contents with new people.
        Depending on which properties have been updated.
        """
        logger.debug(f"Update People Overview")

        if people is not None:
            logger.debug("Updating character page contents with new people\n%s", str(
                people.to_dict("records")))
            self.characterPage.update_contents(
                people=people
            )

        if characters is not None:
            logger.debug("Update relationships/actions with new characters\n%s",
                         str(characters.to_dict("records")))
            self.relationshipPage.update_contents(characters=characters)
            self.actionPage.update_contents(characters=characters)

            if self.update_external is not None:
                self.update_external(
                    characters=characters
                )

    def load(self, people: pd.DataFrame = None, characters: pd.DataFrame = None, relationships: pd.DataFrame = None, character_actions: pd.DataFrame = None) -> None:
        """Load movie attributes to people manager."""
        self.characterPage.load(people=people, characters=characters)
        self.personPage.load(people=people)
        self.relationshipPage.load(
            characters=characters, relationships=relationships)
        self.actionPage.load(characters=characters,
                             character_actions=character_actions)
