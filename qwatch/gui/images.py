""" Functionality to edit images."""
from functools import partial
from typing import List, Dict

from IPython.display import display
import pandas as pd
from PIL import Image, ImageTk
import sqlalchemy
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
from tkinter.font import Font

from qwatch.gui.utils import TextExtension


class ImagePanel(ttk.Frame):
    def __init__(self, parent: ttk.Frame, images: pd.DataFrame = None, **kwargs):
        ttk.Frame.__init__(
            self, parent,
            style='Card.TFrame',
            **kwargs
        )
        self.images = self.process_images(images) if images is not None else []
        self.index = 0

        ###############################################
        # Control Panel for images
        ###############################################
        self.controlPanel = ttk.Frame(self)

        img_label = ttk.Label(
            self.controlPanel, text="Images",
            width=10,  # height=1
        )
        img_label.pack(side="top", pady=5, padx=0)
        f = Font(img_label, img_label.cget("font"))
        f.configure(underline=True)
        img_label.configure(font=f)

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

    def process_images(self, images: pd.DataFrame):
        """Convert Images to usable form."""

        return [
            {
                "ID": image["FILENAME"],
                "DIR": image["DIR"],
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

    def load(self, images: pd.DataFrame):
        self.images = self.process_images(images)
        self.index = 0

        self.clear_image_panel()
        self.load_image()

    def get_items(self) -> pd.DataFrame:
        return pd.DataFrame([{
            **img,
            "CAPTION": img["CAPTION"].get()
        } for img in self.images])

    def load_image(self):
        if len(self.images) == 0:
            ttk.Label(
                self.imagePanel, text="No Images",
            ).pack()
            return

        image1 = Image.open(self.images[self.index]["FILENAME"])

        panel_height = self.imagePanel.winfo_height()
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
            textvariable=self.images[self.index]["CAPTION"]
        ).pack(side="right", fill="both", expand=True)

        movieImage.pack(side="left")

    def delete_image(self):
        # TODO Remove image from dir

        if len(self.images) == 0:
            return

        del self.images[self.index]

        if self.index == len(self.images):
            self.index -= 1

        self.clear_image_panel()
        self.load_image()

    def increment_index(self, increment):
        def func():

            if len(self.images) == 0:
                return

            if increment < 0 and self.index == 0:
                self.index = len(self.images) - 1
            else:
                self.index = (self.index + increment) % len(self.images)

            self.clear_image_panel()
            self.load_image()
        return func
