import io
import logging

from matplotlib import pyplot as plt
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class RatingsFrame(ttk.Frame):

    def __init__(self, parent: ttk.Frame, ratings: pd.DataFrame = None) -> None:
        ttk.Frame.__init__(self, parent)

        lbl = ttk.Label(self, text="Ratings")
        lbl.pack(side="top", fill=tk.X, expand=True)

        self.contents = ttk.Frame(self)
        self.contents.pack(side="top", fill=tk.BOTH, expand=True)

        self.load(ratings)

    def load(self, ratings):
        # Delete items in contents
        for widgets in self.contents.winfo_children():
            widgets.destroy()

        if ratings is not None:
            ttk.Label(self.contents, text=f"Total Ratings: {ratings.shape[0]:,} Average Rating: {ratings.RATING.mean():.2f}").pack(
                side="top")

            ###############################################
            # Create Plot of Ratings
            ###############################################
            plt.rcParams.update({
                "font.size": 20
            })
            _, ax = plt.subplots(figsize=(15, 6))
            ax.plot(
                ratings.groupby("DATE").RATING.mean().reset_index().DATE,
                ratings.groupby("DATE").RATING.mean().reset_index().RATING,
                color="blue", linewidth=2, label="Mean Rating"
            )
            ax2 = ax.twinx()
            ax2.plot(
                ratings.groupby("DATE").RATING.count().reset_index().DATE,
                ratings.groupby("DATE").RATING.count().reset_index().RATING,
                color="orange", linewidth=2, label="Ratings Count"
            )
            ax2.set_ylabel("Rating Count")
            ax.set_ylabel("Mean Rating")
            ax.set_xlabel("Date")
            ax.legend(loc="upper left", bbox_to_anchor=(0, -0.1))
            ax2.legend(loc="upper right", bbox_to_anchor=(1, -0.1))
            ax.set_title(f"Ratings Over time")

            figure_buffer = io.BytesIO()
            plt.savefig(figure_buffer, format="png")
            im = Image.open(figure_buffer)

            width, height = im.size

            self.update_idletasks()
            IMG_WIDTH = self.contents.winfo_width()

            logger.info(
                f"Ratings winfo width {IMG_WIDTH} ORIGINAL {width}"
            )
            IMG_WIDTH = int(IMG_WIDTH)

            im = im.resize(
                (IMG_WIDTH, int(IMG_WIDTH/width*height)), Image.ANTIALIAS)

            # Self to stop image being garbage collected
            self.next_image = ImageTk.PhotoImage(
                im
            )
            ratings_image = tk.Label(self.contents, image=self.next_image)
            ratings_image.pack(side="bottom")

        else:
            ttk.Label(self.contents, text="No ratings available.").pack(
                side="top")
