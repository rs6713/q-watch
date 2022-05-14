""" Functionality to edit images."""
from functools import partial

from IPython.display import display
from PIL import Image, ImageTk
import sqlalchemy
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
from tkinter.font import Font


class ImagePanel(ttk.Frame):
    def __init__(self, parent, images=None, **kwargs):
        ttk.Frame.__init__(
            self, parent,
            # borderwidth=2,
            style='Card.TFrame',
            **kwargs
        )
        self.images = images or []
        self.index = 0
        self.savedImages = {}

        self.controlPanel = ttk.Frame(self)

        img_label = ttk.Label(
            self.controlPanel, text="Image Selector",
            width=10,  # height=1
        )
        img_label.pack(side="top", pady=5, padx=0)

        f = Font(img_label, img_label.cget("font"))
        f.configure(underline=True)
        img_label.configure(font=f)

        prev = ttk.Button(
            self.controlPanel,
            text="Previous", width=10,  # height=1,
            command=self.increment_index(-1)
        )
        nextt = ttk.Button(
            self.controlPanel,
            text="Next", width=10,  # height=1,
            command=self.increment_index(1)
        )
        delete = ttk.Button(
            self.controlPanel,
            text="Delete", width=10,  # height=1,
            command=self.delete_image
        )

        self.imageDescriptor = ttk.Frame(self.controlPanel)
        self.imageDescriptor.pack(side="top", expand=True, fill="both")

        # self.controlPanel.winfo_children():
        for widget in [prev, nextt, delete]:
            widget.pack(side="bottom", padx=5, pady=(0, 5))

        self.controlPanel.pack(side="left", fill=tk.Y, padx=(5, 0), pady=5)

        self.imagePanel = ttk.Frame(
            self,  # bg="white"
            # highlightbackground="black", highlightthickness=2
        )
        self.imagePanel.pack(
            side="right", expand=True, fill="both",
            padx=5, pady=5
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
            notify = ttk.Label(
                self.imagePanel, text="No Images",

                # height=3, width=10
            )
            notify.pack()
            return

        image1 = Image.open(self.images[self.index])

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

        caption = ""
        if self.images[self.index] in self.savedImages:
            caption = self.savedImages[self.images[self.index]].get(
                "caption", "")

        self.caption = tk.Text(
            self.imagePanel,
            height=3, width=10
        )
        if caption:
            self.caption.insert("1.0", caption)

        movieImage.pack(side="left")
        self.caption.pack(side="right", fill="both", expand=True)

    def delete_image(self):
        # TODO Remove image from dir

        if len(self.images) == 0:
            return

        del self.images[self.index]

        if self.index == len(self.images):
            self.index -= 1

        self.clearImagePanel()
        if len(self.images) > 0:
            self.loadImage()
        else:
            notify = ttk.Label(
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
