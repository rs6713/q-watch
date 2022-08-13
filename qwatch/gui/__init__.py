""" Central Scraper GUI. """
from functools import partial
import io
import logging
from pathlib import Path
import os
from typing import Callable, Dict, List, Tuple

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import seaborn as sns
import spacy
import sqlalchemy
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
from tkinter.font import Font, nametofont

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
from qwatch.io.output import delete_movie, save_movie
from qwatch.scrape.images import scrape_movie_images
from qwatch.scrape import scrape_movie_information
from qwatch.gui.defaults import DEFAULTS
from qwatch.gui.images import ImagePanel
from qwatch.gui.menus import MenuMultiSelector, MenuSingleSelector, ChecklistBox
from qwatch.gui.people import PeopleManagementPanel
from qwatch.gui.ratings import RatingsFrame
from qwatch.gui.utils import EditableList, get_options, TextExtension
from qwatch.utils import describe_obj

nlp_model = spacy.load('en_core_web_md')

logger = logging.getLogger(__name__)


class MovieSelector(tk.Toplevel):
    def __init__(self, select_action: Callable):
        """ Popup window, to select movie from database to load."""
        tk.Toplevel.__init__(self)
        self.wm_title("Open Movie")

        # Load movies to search
        self.load_movies()

        movie_selected = tk.StringVar()
        movie_selected.set("Select Movie")
        movie_selector = tk.OptionMenu(
            self, movie_selected, *self.movies.values()
        )
        movie_selector.config(width=30)
        movie_selector.pack(side="left", padx=(0, 5), fill=tk.X, expand=True)

        def select_movie():
            """ On click, load this movie."""
            selected_movie_id = [
                k for k, v in self.movies.items()
                if v == movie_selected.get()
            ]
            if len(selected_movie_id):
                select_action(movie_id=selected_movie_id[0])
                self.destroy()

        # Button to click to open movie selected from option menu
        movie_selector_button = ttk.Button(
            self,
            text="Open",
            command=select_movie,
            style='Accent.TButton'
        )
        movie_selector_button.pack(side="right")

    def load_movies(self):
        """ Getting possible movie properties """
        engine = _create_engine()
        with engine.connect() as conn:
            self.movies = get_movies_ids(conn)


class MovieSearch(tk.Toplevel):
    def __init__(self, load_movie: Callable):
        """Pop up Window to search for new movie."""
        tk.Toplevel.__init__(self, pady=5, padx=5)
        self.wm_title("Search Movie")

        self.get_available_movies()
        self.load_movie = load_movie

        # Movie Title
        movie_title_entry = ttk.Entry(
            self, width=40
        )
        movie_title_entry.grid(row=0, column=0, sticky="w",
                               padx=0, columnspan=2)

        ttk.Label(self, text="Year").grid(
            column=0, row=1, sticky="w", padx=(0, 5))
        year_entry = ttk.Entry(self)
        year_entry.grid(
            row=1, column=1, sticky="ew"
        )

        def check_movie():
            """ Check if the entered title matches any pre-existing movies."""
            title = movie_title_entry.get()
            year = int(year_entry.get()) if year_entry.get() else None

            title_matches = self.check_title_matches(title, year)
            if len(title_matches) > 0:
                self.load_movie_warning(title_matches, title, year)
            else:
                # Load movie
                self.load_movie(movie_title=title, movie_year=year)
            self.destroy()

        # Search button, to search movie (scrape then load details in UI)
        search_button = ttk.Button(
            self,
            text="Search",
            command=check_movie,
        )
        search_button.grid(column=3, row=0, padx=(5, 0))

    def check_title_matches(self, title: str, year: int = None):
        """ Check that there are no similarly named pre-existing movies."""
        potential_matches = [
            (movie_id, movie_title)
            for movie_id, (movie_title, movie_year) in self.movies.items()
            if nlp_model(movie_title).similarity(nlp_model(title)) > 0.9 and (year is None or movie_year == year)
        ]
        return potential_matches

    def get_available_movies(self):
        """ Getting possible movie properties """
        engine = _create_engine()
        with engine.connect() as conn:
            self.movies = get_movies_ids(conn, with_year=True)

    def load_movie_warning(self, movie_matches: List[Tuple[int, str]], title: str, year: int = None):
        """
        Popup warning when there is a movie named similar to title typed.

        Params
        ------
        movies:
            Movies from db that are similar in name.
        title: str
            Movie title entered to create-new movie.
        year: int
            Moive year if specified
        """
        edit_movie_popup = tk.Toplevel(pady=5, padx=5)
        edit_movie_popup.wm_title(
            "Warning! Movie title closely matches pre-existing movies")

        txt = ttk.Label(
            edit_movie_popup,
            wraplength=300,
            text=f"Similar Movies to '{title}'{('for year ' + str(year)) if year is not None else ''} pre-exist. Either edit or continue to create new"
        )
        txt.grid(row=0, column=0, columnspan=2, sticky="ew")

        for i, (movie_id, movie_title) in enumerate(movie_matches):
            movie_label = ttk.Label(edit_movie_popup, text=movie_title)
            movie_label.grid(row=i+1, column=0, padx=(0, 5))

            # Button to choose to load pre-existing movie to edit
            def load_existing_movie(movie_id):
                def func():
                    self.load_movie(movie_id=movie_id)
                    edit_movie_popup.destroy()
                return func

            movie_button = ttk.Button(
                edit_movie_popup, text="Edit",
                command=load_existing_movie(movie_id=movie_id)
            )
            movie_label.grid(row=1+i, column=0, sticky=tk.W)
            movie_button.grid(row=1+i, column=1, sticky=tk.E, padx=(5, 0))

        def load_new_movie():
            self.load_movie(movie_title=title, movie_year=year)
            edit_movie_popup.destroy()

        # Not concerned by name similarity. Create the new movie
        continue_button = ttk.Button(
            edit_movie_popup, text="Continue",
            command=load_new_movie,
            style='Accent.TButton'
        )
        continue_button.grid(column=1, sticky=tk.E, row=len(movie_matches)+1)


class OptionsMenu(tk.Toplevel):
    def __init__(self, options: Dict):
        """Pop up Window to search for new movie."""
        tk.Toplevel.__init__(self, pady=5, padx=5)

        for i, (option, var) in enumerate(options.items()):
            ttk.Label(self, text=option).grid(
                row=i, padx=(0, 5), column=0, sticky="w")
            if not isinstance(var, tk.IntVar):
                ttk.Entry(
                    self,
                    textvariable=var,
                    width=10
                ).grid(row=i, column=1)
            else:
                ttk.Checkbutton(
                    self,
                    var=var,
                    text=option,
                    onvalue=1, offvalue=0, width=10
                ).grid(row=i, column=1)


class MovieWindow():
    detail_categories = [
        "BOX_OFFICE",
        "BUDGET",
        "YEAR",
        "CERTIFICATE",
        "LANGUAGE",
        "COUNTRY",
        "RUNTIME",
        "TRAILER",
    ]

    def get_movie_properties(self):
        """ Getting possible movie properties """
        engine = _create_engine()
        with engine.connect() as conn:
            self.representations = get_representations(conn)
            self.tropes = get_tropes(conn)
            self.genres = get_genres(conn)
            self.movies = get_movies_ids(conn)
            self.types = _get_movie_properties(conn, "TYPE", None)
            self.ages = _get_movie_properties(conn, "AGE", None)
            self.intensities = _get_movie_properties(conn, "INTENSITY", None)
            self.sources = _get_movie_properties(conn, "SOURCE", None)

    def configure_root(self):
        """ Configure properties of app window."""
        self.root = tk.Tk()
        # self.root.grid(row = 0,column = 0, sticky = "nsew")

        for i in np.arange(10):
            self.root.columnconfigure(i, weight=1)
            self.root.rowconfigure(i, weight=1)
        self.root.title("Q-Watch Movie Loader")

        # Custom Styling
        self.root.tk.call(
            "source",
            os.path.join(
                Path(__file__).parent.parent.parent,
                "Azure-ttk-theme",
                "azure.tcl"
            )
        )
        self.root.tk.call("set_theme", "light")

        self.defaultFont = nametofont("TkDefaultFont")
        self.defaultFont.configure(
            family=DEFAULTS["FONT_FAMILY"],
            size=DEFAULTS["FONT_SIZE"],
            weight=DEFAULTS["FONT_WEIGHT"],
        )

    def configure_menu(self):
        """ Configure Root Menu."""
        self.menubar = tk.Menu(self.root)
        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.fileMenu)
        self.fileMenu.add_command(label="New", command=self.refresh)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(
            label='Search', command=partial(MovieSearch, self.load_movie))
        self.fileMenu.add_command(
            label='Open', command=partial(MovieSelector, self.load_movie))
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Save', command=self.save_movie)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Delete', command=self.delete_movie)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(
            label='Options', command=partial(OptionsMenu, self.OPTIONS))
        self.fileMenu.add_command(label='Exit', command=self.root.destroy)

    def refresh(self):
        """Refresh UI."""
        logger.info("Refreshing UI")
        self.update_contents({
            "SOURCES": pd.DataFrame([]),
            "QUOTES": pd.DataFrame([]),
        })

    def load_movie(self, movie_title: str = None, movie_id: int = None, movie_year: str = None, limit: int = 1) -> None:
        """
        Either load movie_id if supplied, or search for movie_title, scraping.

        Params
        ------
        movie_title: str

        movie_id: int

        movie_year: str

        limit: int
        """
        if movie_title is not None:
            logger.info("Loading New Movie: %s", movie_title)
            # Get movie images
            image_dirs = scrape_movie_images(
                movie_title, movie_year=movie_year, limit=int(self.OPTIONS["NUM_IMAGES_SCRAPE"].get()))
            images = pd.DataFrame([{
                "FILENAME": img
            } for img in image_dirs])

            # Get Wikipedia scraped movie information
            movie_information = scrape_movie_information(
                movie_title, movie_year, options=self.OPTIONS, open_urls=self.OPTIONS.get(
                    "OPEN_URLS")
            )

            movie = {
                "TITLE": movie_title,
                "IMAGES": images,
                **movie_information
            }

        # Load movie to edit
        elif movie_id is not None:
            logger.info("Loading Existing Movie %d", movie_id)
            engine = _create_engine()
            with engine.connect() as conn:
                movie = get_movie(conn, movie_id)

        logger.debug("Updating contents of gui with movie:\n%s", movie)
        self.update_contents(movie)

    def update_external(self, characters: pd.DataFrame = None, **kws):
        """Update global attrs in people management."""
        if characters is not None:
            # If character has been deleted need to remove character reference
            quotes = self.datastore["QUOTES"].get_items()
            logger.debug("Update external quotes: \n%s, due to new characters \n%s",
                         quotes, characters
                         )
            quotes.loc[
                ~quotes.CHARACTER_ID.isin(characters.ID.values),
                "CHARACTER_ID"
            ] = -1  # Can't be None, or converts col to float
            self.datastore["QUOTES"].load(
                options={
                    "CHARACTER_ID": get_options(
                        characters, "ID", ["FIRST_NAME", "LAST_NAME"]
                    )
                },
                items=quotes
            )

    def delete_movie(self):
        """Delete movie object from db."""
        if self.movie["ID"].get() is None or not self.movie["ID"].get():

            messagebox.showerror(
                "showerror",
                "Could not delete movie that doesn't exist in db!"
            )
        else:
            delete_popup = tk.Toplevel(pady=5, padx=5)
            delete_popup.wm_title(
                f"Delete Movie {self.movie['TITLE'].get()}"
            )

            txt = ttk.Label(
                delete_popup,
                wraplength=300,
                text="Are you sure you want to delete?"
            )
            txt.grid(row=0, column=0, columnspan=2, sticky="ew")

            def delete_movie_func():
                """ Delete movie in db, clear movie_entry gui, destroy window."""
                engine = _create_engine()
                with engine.connect() as conn:
                    delete_movie(conn, movie_id=self.movie["ID"].get())
                self.refresh()
                delete_popup.destroy()

            ttk.Button(
                delete_popup, text="Delete",
                command=delete_movie_func
            ).grid(row=1, column=1, padx=(5, 0))

            ttk.Button(
                delete_popup, text="Cancel",
                command=delete_popup.destroy
            ).grid(row=1, column=0, padx=(0, 5))

    def save_movie(self):
        """ Create movie object and save."""
        movie = {}
        for prop in self.movie.keys():
            try:
                movie[prop] = self.movie[prop].get()
            except Exception as e:
                logger.warning("Failed to get property for %s", prop)
                raise e

        for menu in ["GENRES", "TROPE_TRIGGERS", "REPRESENTATIONS", "TYPES"]:
            try:
                movie[menu] = self.datastore[menu].get_selected_options()
            except Exception as e:
                logger.warning("Failed to get options from %s", menu)
                raise e

        for lst in ["SOURCES", "QUOTES", "IMAGES"]:
            try:
                movie[lst] = self.datastore[lst].get_items()
                if movie[lst] is None:
                    movie[lst] = []
                else:
                    movie[lst] = movie[lst].to_dict("records")
            except Exception as e:
                logger.warning("Failed to get items for %s", lst)
                raise e

        movie = {
            **movie,
            **self.datastore["PEOPLE"].get_items()
        }

        engine = _create_engine()
        with engine.connect() as conn:
            logger.info("Saving constructed movie object:\n%s", str(movie))
            self.movie["ID"].set(save_movie(conn, movie))

    def update_contents(self, movie: Dict) -> None:
        """ Update contents of UI with self.movie."""

        logger.info(
            f"Updating Movie Contents \n{describe_obj(movie)}")

        for k in self.movie.keys():
            if k in movie:
                self.movie[k].set(movie[k])
            else:
                if isinstance(self.movie[k], tk.StringVar):
                    self.movie[k].set("")
                else:
                    self.movie[k].set(-1)  # -1 is the invalid value

        for menu in ["GENRES", "TROPE_TRIGGERS", "REPRESENTATIONS", "TYPES"]:
            self.datastore[menu].load(
                movie.get(menu, None)
            )

        # Images, People, sources, quotes, ratings
        self.datastore["SOURCES"].load(
            items=movie.get("SOURCES", None)
        )

        characters = movie.get("CHARACTERS", pd.DataFrame([]))
        self.datastore["QUOTES"].load(
            items=movie.get("QUOTES", None),
            options={
                "CHARACTER_ID": get_options(
                    characters, "ID", ["FIRST_NAME", "LAST_NAME"]
                )
            }
        )
        self.datastore["IMAGES"].load(images=movie.get("IMAGES", None))
        self.ratings_frame.load(movie.get("RATINGS", None))
        self.datastore["PEOPLE"].load(
            people=movie.get("PEOPLE", None),
            characters=movie.get("CHARACTERS", None),
            relationships=movie.get("RELATIONSHIPS", None),
            character_actions=movie.get("CHARACTER_ACTIONS", None)
        )

    def __init__(self):
        self.get_movie_properties()
        self.configure_root()

        self.OPTIONS = {
            "NUM_IMAGES_SCRAPE": tk.StringVar(value="5"),
            "NUM_CAST_SCRAPE": tk.StringVar(value="8"),
            "NUM_WRITER_SCRAPE": tk.StringVar(value="5"),
            "NUM_DIRECTOR_SCRAPE": tk.StringVar(value="3"),
            "NUM_QUOTES_SCRAPE": tk.StringVar(value="10"),
            "OPEN_URLS": tk.IntVar(value=1),
        }
        self.configure_menu()

        self.movie = {
            "ID": tk.IntVar(),
            "TITLE": tk.StringVar(),
            "AGE": tk.IntVar(),
            "INTENSITY": tk.IntVar(),
            "SUMMARY": tk.StringVar(),
            "BIO": tk.StringVar(),
            "OPINION": tk.StringVar(),
            "BOX_OFFICE": tk.StringVar(),
            "BUDGET": tk.StringVar(),
            "YEAR": tk.StringVar(),
            "RUNTIME": tk.StringVar(),
            "LANGUAGE": tk.StringVar(),
            "COUNTRY": tk.StringVar(),
            "TRAILER": tk.StringVar(),
            "CERTIFICATE": tk.StringVar()
        }
        self.datastore = {}  # Hold panels/widgets from which can fetch entered data

        ###################################################
        # Text Entries for:
        #   Summary, Bio, Opinion
        ###################################################
        describeFrame = ttk.Frame(self.root)
        ttk.Entry(describeFrame, textvariable=self.movie["TITLE"]).pack(
            side=tk.TOP, pady=5, expand=1, fill=tk.X)
        ttk.Label(describeFrame, text="Summary").pack(
            side=tk.TOP, pady=(0, 5), expand=1, fill=tk.X)
        TextExtension(
            describeFrame,  # height=10,  # width=50,
            height=4,  # wrap=tk.WORD,
            textvariable=self.movie["SUMMARY"],
        ).pack(
            side=tk.TOP, pady=(0, 5), expand=1, fill=tk.BOTH)
        ttk.Label(describeFrame, text="Bio").pack(
            side=tk.TOP, pady=(0, 5), expand=1, fill=tk.X)
        TextExtension(
            describeFrame, height=3, textvariable=self.movie["BIO"]
        ).pack(side=tk.TOP, expand=1, fill=tk.X)

        describeFrame.grid(row=0, column=0, columnspan=2, padx=5,
                           pady=(0, 5), rowspan=3, sticky="nsew")

        ######################################################
        # Movie Details section
        # Text Opinion Entry
        # Entries for shortform responses detail_categories
        # Dropdown for intensity/age
        ######################################################
        detailsFrame = ttk.Frame(self.root)

        # Opinion label
        ttk.Label(detailsFrame, text="My Opinion").pack(
            side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5))
        TextExtension(
            detailsFrame, height=2, textvariable=self.movie["OPINION"]
        ).pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5))

        # Rows of details
        f = None
        n_items_row = 4
        for i, detail in enumerate(self.detail_categories):
            if i % n_items_row == 0:
                f = ttk.Frame(detailsFrame)
                f.pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5))

            lf = ttk.LabelFrame(f, text=detail)
            ttk.Entry(lf, textvariable=self.movie[detail]).pack(
                side="top",
                fill=tk.X,
                expand=True,
                pady=1, padx=1
            )
            lf.pack(
                side="left",
                fill=tk.X,
                expand=True,
                pady=1, padx=((0, 5) if not (i % n_items_row == (n_items_row - 1)) and (i != (len(self.detail_categories)-1)) else 0)
            )

        ################################################################
        # Dropdown selectors for movie properties - rating, age
        ################################################################
        dropdownFrame = ttk.Frame(detailsFrame)
        MenuSingleSelector(
            dropdownFrame, "Intensity", self.intensities, var=self.movie["INTENSITY"]
        ).pack(side="left", fill=tk.X, expand=True, padx=(0, 5))

        MenuSingleSelector(
            dropdownFrame, "Age", self.ages, var=self.movie["AGE"]
        ).pack(side="left", fill=tk.X, expand=True)

        dropdownFrame.pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5))

        detailsFrame.grid(
            column=0, columnspan=2, row=3, rowspan=4, sticky="nsew", padx=5
        )

        #####################################################
        # COLUMN 2 --> Checkbox lists, image selector
        #####################################################
        checklist_container = ttk.Frame(self.root)
        checklist_container.grid(
            column=2, row=0, columnspan=6, rowspan=3, sticky="nsew", pady=5, padx=5)

        self.datastore["REPRESENTATIONS"] = ChecklistBox(
            checklist_container, "Representations", self.representations,
            radio="MAIN", id_name="REPRESENTATION_ID"
        )
        self.datastore["TROPE_TRIGGERS"] = ChecklistBox(
            checklist_container, "Tropes", self.tropes, id_name="TROPE_TRIGGER_ID"
        )
        self.datastore["GENRES"] = ChecklistBox(
            checklist_container, "Genres", self.genres, id_name="GENRE_ID"
        )
        self.datastore["TYPES"] = ChecklistBox(
            checklist_container, "Types", self.types,
            radio="EXPLICIT", id_name="TYPE_ID"
        )
        self.datastore["GENRES"].pack(
            side="left", expand=1, fill=tk.BOTH, padx=(0, 5)
        )
        self.datastore["TROPE_TRIGGERS"].pack(
            side="left", expand=1, fill=tk.BOTH, padx=(0, 5)
        )
        self.datastore["REPRESENTATIONS"].pack(
            side="left", expand=1, fill=tk.BOTH, padx=(0, 5)
        )
        self.datastore["TYPES"].pack(
            side="left", expand=1, fill=tk.BOTH
        )
        # self.datastore["GENRES"].grid(
        #     column=2, row=0, rowspan=3, columnspan=1, sticky="nsew", pady=5, padx=(0, 3))
        # self.datastore["TROPES"].grid(
        #     column=3, row=0, rowspan=3, columnspan=1, sticky="nsew", pady=5, padx=(0, 3))
        # self.datastore["REPRESENTATIONS"].grid(
        #     column=4, row=0, rowspan=3, columnspan=1, sticky="nsew", pady=5)

        self.datastore["IMAGES"] = ImagePanel(self.root)
        self.datastore["IMAGES"].grid(
            column=2, row=3, columnspan=6, rowspan=4,
            sticky="nsew"
        )
        ##############################################################
        # CharacterFrame for People/Characters/Relationships in Movie
        ##############################################################
        self.datastore["PEOPLE"] = PeopleManagementPanel(
            self.root, update_external=self.update_external
        )
        self.datastore["PEOPLE"].grid(
            column=0, row=7, columnspan=8, rowspan=3,
            sticky="nsew"
        )

        #############################################################
        # Frame for Sources, and their votes
        #############################################################
        self.notebook = ttk.Notebook(self.root)
        self.datastore["SOURCES"] = EditableList(
            self.notebook, "Sources",
            item_map={
                "SOURCE_ID": "DROPDOWN",
                # "URL": "ENTRY",
                "COST": "NUM_ENTRY",
                "MEMBERSHIP_INCLUDED": "BOOLEAN",
            },
            options={"SOURCE_ID": get_options(
                self.sources, "ID", ["LABEL", "REGION"], sep=" - ")}
        )

        # self.datastore["SOURCES"].grid(
        #     row=0, rowspan=7, columnspan=2, column=8, sticky="nsew", padx=3, pady=3
        # )

        ##############################################################
        # Frame for Quotes, ratings
        ##############################################################
        self.datastore["QUOTES"] = EditableList(
            self.notebook,
            "Quotes",
            # items=self.movie["quotes"],
            item_map={
                "QUOTE": "ENTRY", "CHARACTER_ID": "DROPDOWN"
            },
            group="QUOTE_ID",
            options={"CHARACTER_ID": pd.DataFrame([])},
        )

        self.notebook.add(self.datastore["QUOTES"], text="Quotes")
        self.notebook.add(self.datastore["SOURCES"], text="Sources")
        self.notebook.grid(
            row=0, rowspan=7, columnspan=2, column=8, sticky="nsew", padx=3, pady=3
        )

        # self.datastore["QUOTES"].grid(
        #     row=0, rowspan=3, columnspan=3, column=5, sticky="nsew", padx=3, pady=3
        # )

        self.ratings_frame = RatingsFrame(self.root)

        self.ratings_frame.grid(column=8, columnspan=2, row=7,
                                rowspan=3, sticky="nsew", padx=3, pady=3)

        self.root.config(menu=self.menubar)
        self.root.mainloop()


if __name__ == "__main__":
    MovieWindow()

    # "sources": pd.DataFrame([
    #     [1, "Netflix", "www.netflix.com", "US", None, 1],
    #     [4, "Amazon", None, "UK", 3.99, 0]
    # ], columns=["ID", "LABEL", "URL", "REGION", "COST", "MEMBERSHIP_INCLUDED"]),
    # "ratings": pd.DataFrame([
    #     [4, "2022-02-01"],
    #     [3, "2022-02-01"],
    #     [2, "2022-02-02"],
    #     [2, "2022-02-02"],
    #     [4, "2022-02-03"],
    #     [4, "2022-02-03"],
    # ], columns=["RATING", "DATE"]),
    # "quotes": pd.DataFrame([
    #     [1, "I'm not perverted! I get good grades! I go to church! I'm a cheerleader.", 1],
    #     [2, "I too was once a gay.", 0]
    # ], columns=["ID", "QUOTE", "CHARACTER_ID"]),
    # "characters": pd.DataFrame([
    #     [1, 1, "Megan", "Bloomfield"],
    #     [2, 2, "Graham", "Eaton"],
    # ], columns=["CHARACTER_ID", "ACTOR_ID", "FIRST_NAME", "LAST_NAME"])
    # props = ["age", "summary", "year",
    #          "language", "country", "running_time"]
    # print("Update_contents: \n", self.movie)
    # for prop in props:
    #     if prop in self.movie:
    #         if hasattr(self, prop):
    #             getattr(self, prop).insert(
    #                 tk.END, self.movie[prop])
    #         else:
    #             print(f"No {prop} console item")

    # if "images" in self.movie:
    #     self.datastore["images"].loadImages(self.movie["images"])
    # @staticmethod
    # def alert(err_type, msg):
    #     if err_type == "warning":
    #         messagebox.showinfo('Movie Submission Warning', msg)
    #         messagebox.askyesno("askyesno", "Continue submitting Movie?")
    #     if err_type == "error":
    #         messagebox.showerror(
    #             "showerror", "Movie Entry is Invalid:\n" + msg)

    # def search_movie(self):
    #     """Pop up Window to search for new movie."""
    #     new_movie_popup = tk.Toplevel(pady=5, padx=5)
    #     new_movie_popup.wm_title("Search Movie")

    #     # Movie Title
    #     movie_title_entry = ttk.Entry(
    #         new_movie_popup,
    #         bg="white", fg="black", width=40
    #     )
    #     movie_title_entry.pack(side="left")

    #     def load_movie():
    #         """ Check if the entered title matches any pre-existing movies."""
    #         title = movie_title_entry.get()

    #         title_matches = self.check_title_matches(title)
    #         if len(title_matches) > 0:
    #             self.load_movie_warning(title_matches, title)
    #         else:
    #             self.load_movie(movie_title=title)
    #         new_movie_popup.destroy()

    #     # Search button, to search movie (scrape then load details in UI)
    #     search_button = ttk.Button(
    #         new_movie_popup,
    #         text="Search",
    #         command=load_movie,
    #         padx=5, pady=2
    #     )
    #     search_button.pack(side="left", padx=(5, 0))
# def open_movie(self):
#     """ Popup window, to select movie from database to load."""
#     open_movie_popup = tk.Toplevel(pady=5, padx=5)
#     open_movie_popup.wm_title("Open Movie")

#     movie_selected = tk.StringVar()
#     movie_selected.set("Select Movie")
#     movie_selector = tk.OptionMenu(
#         open_movie_popup, movie_selected, *self.movies.values()
#     )
#     movie_selector.config(width=30)
#     movie_selector.pack(side="left", padx=(0, 5), fill=tk.X, expand=True)

#     def select_movie():
#         """ On click, load this movie."""
#         selected_movie_id = [
#             k for k, v in self.movies.items() if v == movie_selected.get()]
#         if len(selected_movie_id):
#             self.load_movie(movie_id=selected_movie_id[0])
#             open_movie_popup.destroy()

#     # Button to click to open movie selected from option menu
#     movie_selector_button = ttk.Button(
#         open_movie_popup,
#         text="Open",
#         command=select_movie,
#         padx=5, pady=2
#     )
#     movie_selector_button.pack(side="right")
