""" Central Scraper GUI. """
from functools import partial
import io
import logging
from pathlib import Path
import os
from typing import Callable, Dict, List, Tuple

from matplotlib import pyplot as plt
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
from qwatch.scrape.images import download_images
from qwatch.scrape.wikipedia import scrape_movie_information
from qwatch.gui.defaults import DEFAULTS
from qwatch.gui.images import ImagePanel
from qwatch.gui.menus import MenuMultiSelector, MenuSingleSelector, ChecklistBox
from qwatch.gui.people import PeopleManagementPanel
from qwatch.gui.ratings import RatingsFrame
from qwatch.gui.utils import EditableList, get_options, TextExtension

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
            padx=5, pady=2
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
        tk.Toplevel(self, pady=5, padx=5)
        self.wm_title("Search Movie")

        self.get_available_movies()
        self.load_movie = load_movie

        # Movie Title
        movie_title_entry = ttk.Entry(
            self,
            bg="white", fg="black", width=40
        )
        movie_title_entry.pack(side="left")

        def check_movie():
            """ Check if the entered title matches any pre-existing movies."""
            title = movie_title_entry.get()

            title_matches = self.check_title_matches(title)
            if len(title_matches) > 0:
                self.load_movie_warning(title_matches, title)
            else:
                # Load movie
                self.load_movie(movie_title=title)
            self.destroy()

        # Search button, to search movie (scrape then load details in UI)
        search_button = ttk.Button(
            self,
            text="Search",
            command=check_movie,
            padx=5, pady=2
        )
        search_button.pack(side="left", padx=(5, 0))

    def check_title_matches(self, title: str):
        """ Check that there are no similarly named pre-existing movies."""
        potential_matches = [
            (movie_id, movie_title)
            for movie_id, movie_title in self.movies.items()
            if nlp_model(movie_title).similarity(nlp_model(title)) > 0.9
        ]
        return potential_matches

    def get_available_movies(self):
        """ Getting possible movie properties """
        engine = _create_engine()
        with engine.connect() as conn:
            self.movies = get_movies_ids(conn)

    def load_movie_warning(self, movie_matches: List[Tuple(int, str)], title: str):
        """
        Popup warning when there is a movie named similar to title typed.

        Params
        ------
        movies: 
            Movies from db that are similar in name.
        title: str
            Movie title entered to create-new movie.
        """
        edit_movie_popup = tk.Toplevel(pady=5, padx=5)
        edit_movie_popup.wm_title(
            "Warning! Movie title closely matches pre-existing movies")

        txt = ttk.Label(
            edit_movie_popup,
            wraplength=300,
            text=f"Similar Movies to '{title}' pre-exist. Either edit or continue to create new"
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
            self.load_movie(movie_title=title)
            edit_movie_popup.destroy()

        # Not concerned by name similarity. Create the new movie
        continue_button = ttk.Button(
            edit_movie_popup, text="Continue",
            command=load_new_movie,
            padx=2, pady=2
        )
        continue_button.grid(column=1, sticky=tk.E, row=len(movie_matches)+1)


class MovieWindow():
    detail_categories = [
        "box_office",
        "budget",
        "year",
        "age",
        "language",
        "country",
        "running_time",
        "trailer",
    ]

    def get_movie_properties(self):
        """ Getting possible movie properties """
        engine = _create_engine()
        with engine.connect() as conn:
            self.representations = get_representations(conn)
            self.tropes = get_tropes(conn)
            self.genres = get_genres(conn)
            self.movies = get_movies_ids(conn)
            self.ages = _get_movie_properties(conn, "AGE", None)
            self.intensities = _get_movie_properties(conn, "INTENSITY", None)
            self.sources = _get_movie_properties(conn, "SOURCE", None, addit_props=[
                "COST", "MEMBERSHIP_INCLUDED"
            ])

    def configure_root(self):
        """ Configure properties of app window."""
        self.root = tk.Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
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
        self.fileMenu.add_command(
            label='New', command=partial(MovieSearch, self.load_movie))
        self.fileMenu.add_command(
            label='Open', command=partial(MovieSelector, self.load_movie))
        self.fileMenu.add_command(label='Save', command=self.save_movie)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Exit', command=self.root.destroy)

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
            # Get movie images
            image_dirs = download_images(movie_title, limit=limit)[
                0][movie_title]

            # Get Wikipedia scraped movie information
            movie_information = scrape_movie_information(movie_title)

            movie = {
                "title": movie_title,
                "images": image_dirs,
                **movie_information
            }

        # Load movie to edit
        elif movie_id is not None:
            engine = _create_engine()
            with engine.connect() as conn:
                movie = get_movie(conn, movie_id)

        self.update_contents(movie)

    def save_movie(self):
        pass

    def update_contents(self, movie):
        """ Update contents of UI with self.movie."""

        for k in self.movie.keys():
            if k in movie:
                self.movie[k].set(movie[k])
            else:
                self.movie[k].set(None)

        # Images, People, sources, quotes, ratings
        self.datastore["sources"].load(
            items=movie.get("sources", None)
        )

        characters = movie.get("characters", pd.DataFrame([]))
        self.datastore["quotes"].load(
            items=movie.get("quotes", None),
            options={
                "CHARACTER_ID": get_options(
                    characters, "CHARACTER_ID", ["FIRST_NAME", "LAST_NAME"]
                )
            }
        )
        self.datastore["images"].load(movie.get("images", []))
        self.ratings_frame.load(movie.get("ratings", None))
        self.datastore["people"].load(
            people=movie.get("people", None),
            characters=movie.get("characters", None),
            relationships=movie.get("relationships", None),
            character_actions=movie.get("character_actions", None)
        )

    def __init__(self):
        self.get_movie_properties()
        self.configure_root()
        self.configure_menu()

        self.movie = {
            "age": tk.IntVar(),
            "intensity": tk.IntVar(),
            "summary": tk.StringVar(),
            "bio": tk.StringVar(),
            "opinion": tk.StringVar(),
            "box_office": tk.StringVar(),
            "budget": tk.StringVar(),
            "year": tk.StringVar(),
            "running_time": tk.StringVar(),
            "language": tk.StringVar(),
            "country": tk.StringVar(),
            "trailer": tk.StringVar(),
        }
        self.datastore = {}  # Hold panels/widgets from which can fetch entered data

        ###################################################
        # Text Entries for:
        #   Summary, Bio, Opinion
        ###################################################
        describeFrame = ttk.Frame(self.root)
        ttk.Label(describeFrame, text="Summary").pack(
            side=tk.TOP, pady=(0, 5), expand=1, fill=tk.X)
        TextExtension(
            describeFrame,  # height=10,  # width=50,
            height=10,  # wrap=tk.WORD,
            textvariable=self.movie["summary"],
        ).pack(
            side=tk.TOP, pady=(0, 5), expand=1, fill=tk.BOTH)
        ttk.Label(describeFrame, text="Bio").pack(
            side=tk.TOP, pady=(0, 5), expand=1, fill=tk.X)
        TextExtension(
            describeFrame, height=3, textvariable=self.movie["bio"]
        ).pack(side=tk.TOP, expand=1, fill=tk.X)

        describeFrame.grid(row=0, column=0, columnspan=2, padx=5,
                           pady=(0, 5), rowspan=3, sticky="ewns")

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
            detailsFrame, height=3, textvariable=self.movie["opinion"]
        ).pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5))

        # Rows of details
        f = None
        for i, detail in enumerate(self.detail_categories):
            if i % 3 == 0:
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
                pady=1, padx=((0, 5) if not (i % 3 == 2) and (i != (len(self.detail_categories)-1)) else 0)
            )

        ################################################################
        # Dropdown selectors for movie properties - rating, age
        ################################################################
        dropdownFrame = ttk.Frame(detailsFrame)
        MenuSingleSelector(
            dropdownFrame, "Intensity", self.intensities, var=self.movie["intensity"]
        ).pack(side="left", fill=tk.X, expand=True, padx=(0, 5))

        MenuSingleSelector(
            dropdownFrame, "Age", self.ages, var=self.movie["age"]
        ).pack(side="left", fill=tk.X, expand=True)

        dropdownFrame.pack(side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5))

        detailsFrame.grid(
            column=0, columnspan=2, row=3, rowspan=4, sticky="ewns", padx=5
        )

        #####################################################
        # COLUMN 2 --> Checkbox lists, image selector
        #####################################################
        self.datastore["representations"] = ChecklistBox(
            self.root, "Representations", self.representations,
        )
        self.datastore["tropes"] = ChecklistBox(
            self.root, "Tropes", self.tropes,
        )
        self.datastore["genres"] = ChecklistBox(
            self.root, "Genres", self.genres,
        )
        self.datastore["genres"].grid(
            column=2, row=0, rowspan=3, columnspan=1, sticky="nsew", pady=5, padx=(0, 3))
        self.datastore["tropes"].grid(
            column=3, row=0, rowspan=3, columnspan=1, sticky="nsew", pady=5, padx=(0, 3))
        self.datastore["representations"].grid(
            column=4, row=0, rowspan=3, columnspan=1, sticky="nsew", pady=5)

        self.datastore["images"] = ImagePanel(self.root)
        self.datastore["images"].grid(
            column=2, row=3, columnspan=3, rowspan=4,
            sticky="ewns"
        )
        ##############################################################
        # CharacterFrame for People/Characters/Relationships in Movie
        ##############################################################
        self.datastore["people"] = PeopleManagementPanel(self.root)
        self.datastore["people"].grid(
            column=0, row=7, columnspan=8, rowspan=3,
            sticky="ewns"
        )

        #############################################################
        # Frame for Sources, and their votes
        #############################################################
        self.datastore["sources"] = EditableList(
            self.root, "Sources",
            item_map={
                "ID": "DROPDOWN",
                "URL": "ENTRY",
                "COST": "NUM_ENTRY",
                "MEMBERSHIP_INCLUDED": "BOOLEAN",
            },
            options={"ID": get_options(
                self.sources, "ID", ["LABEL", "REGION"], sep=" - ")}
        )

        self.datastore["sources"].grid(
            row=0, rowspan=10, columnspan=2, column=8, sticky="ewns", padx=3, pady=3
        )

        ##############################################################
        # Frame for Quotes, ratings
        ##############################################################
        self.datastore["quotes"] = EditableList(
            self.root,
            "Quotes",
            # items=self.movie["quotes"],
            item_map={
                "QUOTE": "ENTRY", "CHARACTER_ID": "DROPDOWN"
            },
            options={"CHARACTER_ID": pd.DataFrame([])}
            # options={"CHARACTER_ID": get_options(
            #    self.movie["characters"], "CHARACTER_ID", ["FIRST_NAME", "LAST_NAME"])}
        )
        self.datastore["quotes"].grid(
            row=0, rowspan=3, columnspan=3, column=5, sticky="ewns", padx=3, pady=3
        )

        self.ratings_frame = RatingsFrame(self.root)  # , self.movie["ratings"]

        self.ratings_frame.grid(column=5, columnspan=3, row=3,
                                rowspan=4, sticky="ewns", padx=3, pady=3)

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
