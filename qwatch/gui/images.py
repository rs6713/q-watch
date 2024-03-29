""" Functionality to edit images."""
from functools import partial
import logging
import os
from pathlib import Path
from typing import List, Dict

from IPython.display import display
import pandas as pd
from PIL import Image, ImageTk
import sqlalchemy
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
from tkinter.font import Font
from tkinter import filedialog as fd

from qwatch.gui.utils import TextExtension
from qwatch.gui.menus import MenuSingleSelector

logger = logging.getLogger(__name__)


class ImagePanel(ttk.Frame):
    def __init__(self, parent: ttk.Frame, images: pd.DataFrame = None, default_image: int = -1, **kwargs):
        ttk.Frame.__init__(
            self, parent,
            style='Card.TFrame',
            **kwargs
        )
        self.images = self.process_images(images)
        self.index = tk.IntVar(value=0)
        self.default_image = tk.IntVar(value=default_image)

        ###############################################
        # Control Panel for images
        ###############################################
        self.controlPanel = ttk.Frame(self)

        img_label = ttk.Label(
            self.controlPanel, text="Images",
            width=10,  # height=1
        )
        img_label.pack(side="top", pady=5, padx=0)

        ttk.Label(self.controlPanel, textvariable=self.index).pack(side="top")

        f = Font(img_label, img_label.cget("font"))
        f.configure(underline=True)
        img_label.configure(font=f)

        # Select default background image
        self.default_image_container = ttk.Frame(self.controlPanel)
        self.default_image_container.pack(side="top", fill=tk.X, expand=True)

        if self.process_options(images).shape[0]:
            MenuSingleSelector(
                self.default_image_container, "Default Image", self.process_options(images), var=self.default_image
            ).pack(side="top", fill=tk.X, expand=True)

        ttk.Button(
            self.controlPanel,
            text="Previous", width=10,
            command=self.increment_index(-1)
        ).pack(side="bottom", padx=5, pady=(0, 5))
        ttk.Button(
            self.controlPanel,
            text="Next", width=10,
            command=self.increment_index(1)
        ).pack(side="bottom", padx=5, pady=(0, 5))
        ttk.Button(
            self.controlPanel,
            text="Delete", width=10,
            command=self.delete_image
        ).pack(side="bottom", padx=5, pady=(0, 5))

        ttk.Button(
            self.controlPanel, text="Upload", width=10, style="Accent.TButton",
            command=self.select_image
        ).pack(side="bottom", padx=5, pady=(0, 5))

        self.imageDescriptor = ttk.Frame(self.controlPanel)
        self.imageDescriptor.pack(side="top", expand=True, fill="both")

        self.controlPanel.pack(side="left", fill=tk.Y, padx=(5, 0), pady=5)

        ############################################
        # Panel to draw/display images.
        ############################################
        self.imagePanel = ttk.Frame(self)
        self.imagePanel.pack(
            side="right", expand=True, fill="both",
            padx=5, pady=5
        )

        self.load_image()

    def select_image(self):
        """Manually upload images into UI."""
        filetypes = (
            ('PNG', '*.png'),
            ('JPEG', '*.jpg'),
            ('BMP', '*.bmp')
        )

        filenames = fd.askopenfilenames(
            title='Select Movie Images',
            initialdir='/',
            filetypes=filetypes)

        new_images = pd.DataFrame([
            {"FILENAME": f}
            for f in filenames
        ])

        self.images = [
            *self.images,
            *self.process_images(new_images)
        ]

    def process_options(self, images: pd.DataFrame):
        if images is None:
            return pd.DataFrame(columns=["ID", "LABEL"])

        return pd.DataFrame(
            [
                {"ID": i, "LABEL": i}
                for i, img in enumerate(images.to_dict("records"))
            ]
        )

    def process_images(self, images: pd.DataFrame):
        """Convert Images to usable form."""

        if images is None:
            return []

        return [
            {
                "ID": image.get("ID", 0),
                "FILENAME": image["FILENAME"],
                "CAPTION": tk.StringVar(value=image.get("CAPTION", ""))
            }
            for image in images.to_dict("records")
        ]

    def clear_image_panel(self):
        """Clear all image descriptors, and displayed images."""
        for widgets in self.imagePanel.winfo_children():
            widgets.destroy()
        for widgets in self.imageDescriptor.winfo_children():
            widgets.destroy()

    def load(self, images: pd.DataFrame = None, default_image: int = None):
        self.images = self.process_images(images)
        self.default_image.set(default_image or -1)
        self.index.set(0)

        self.clear_image_panel()
        self.load_image()

        # Reload image selector
        for widgets in self.default_image_container.winfo_children():
            widgets.destroy()

        if self.process_options(images).shape[0]:
            MenuSingleSelector(
                self.default_image_container, "Default Image", self.process_options(images), var=self.default_image
            ).pack(side="top", fill=tk.X, expand=True)

    def get_items(self) -> pd.DataFrame:
        items = pd.DataFrame([{
            **img,
            "CAPTION": img["CAPTION"].get(),
            "DEFAULT_IMAGE": self.default_image.get() == i
        } for i, img in enumerate(self.images)
            if img["CAPTION"].get()
        ])
        if items.shape[0] != len(self.images):
            logger.warning(
                "%d/%d images could not be saved due to lack of captions",
                len(self.images)-items.shape[0], len(self.images)
            )
        return items

    def load_image(self):
        if len(self.images) == 0:
            ttk.Label(
                self.imagePanel, text="No Images",
            ).pack()
            return

        # Image is stored in db, src/static/movie-picutres
        if self.images[self.index.get()]["ID"] != 0:
            image_path = os.path.join(
                Path(__name__).parent.parent.parent,
                "website", "src", "static", "movie-pictures",
                self.images[self.index.get()]["FILENAME"]
            )
        # image is freshly scraped
        else:
            image_path = self.images[self.index.get()]["FILENAME"]
        logger.debug(
            f"Trying to load image: {image_path}"
        )
        image1 = Image.open(
            image_path
        )

        panel_height = self.imagePanel.winfo_height() - 10
        width, height = image1.size

        img_size = ttk.Label(
            self.imageDescriptor, text=f"({width}, {height})"
        )
        img_size.pack(side="top")

        image1 = image1.resize(
            (int(panel_height/height*width), panel_height), Image.ANTIALIAS)
        next_image = ImageTk.PhotoImage(
            image1
        )

        movieImage = ttk.Label(self.imagePanel, image=next_image)
        movieImage.image = next_image

        TextExtension(
            self.imagePanel,
            height=3, width=10,
            textvariable=self.images[self.index.get()]["CAPTION"]
        ).pack(side="right", fill="both", expand=True)

        movieImage.pack(side="left")

    def delete_image(self):
        # TODO Remove image from dir

        if len(self.images) == 0:
            return

        del self.images[self.index.get()]

        if self.index.get() == len(self.images):
            self.index.set(self.index.get() - 1)

        if self.default_image.get() == self.index.get():
            self.default_image.set(None)

        self.clear_image_panel()
        self.load_image()

    def increment_index(self, increment):
        def func():

            if len(self.images) == 0:
                return

            if increment < 0 and self.index.get() == 0:
                self.index.set(len(self.images) - 1)
            else:
                self.index.set((self.index.get() + increment) %
                               len(self.images))

            self.clear_image_panel()
            self.load_image()
        return func
