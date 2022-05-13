from functools import partial
import logging
import pathlib
import os

import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk

from qwatch.gui.menus import MenuSingleSelector


BIN_IMG = Image.open(os.path.join(
    pathlib.Path(__file__).parent.parent,
    "static", "icons", "bin.png"
))

logger = logging.getLogger(__name__)


class EditableList(tk.Frame):
    def __init__(self, parent: tk.Frame, name: str,  width: int, items: pd.DataFrame = None, item_map: dict = None, options: dict = None):
        """
        Editable List - With deletable and editable items

        """
        tk.Frame.__init__(
            self, parent,   # height=height  # , width=width, height=height,
        )

        self.name = name
        self.item_map = item_map
        self.options = options
        self.canv_width = width
        self.items = self.process_items(items)

        label_frame = tk.Frame(self)
        label = tk.Label(label_frame, text=name)
        label.pack(side="left", fill=tk.X, expand=True)

        btn = tk.Button(
            label_frame, text="New",
            command=self.add_item, padx=5, pady=2
        ).pack(side="right")
        label_frame.pack(side="top", fill=tk.X)

        ################################################
        # Quotes Subframe
        # Canvas with scroll, place subframe inside canvas
        ################################################
        self.scroll_bar = tk.Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # creating a canvas
        self.canv = tk.Canvas(self, width=self.canv_width)
        self.canv.config(relief='flat', bd=2, width=self.canv_width)
        self.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #self.canvas = Canvas(self, width = self.app_sizex, height = self.app_sizey, scrollregion=(0,0,x,y))

        # Will contain quotes
        self.canv_subframe = tk.Frame(self.canv, width=self.canv_width)

        # Load original quotes list
        self.update_list()

        self.canv.create_window(
            (0, 0), window=self.canv_subframe, anchor="nw", tags='my_frame')
        self.canv.bind('<Configure>', self.resize_window)
        parent.update_idletasks()  # So winfo_height dimensions are accurate

        self.canv.config(
            yscrollcommand=self.scroll_bar.set,
            scrollregion=(0, 0, self.canv_width,
                          self.canv_subframe.winfo_height())
        )

        self.scroll_bar.config(command=self.canv.yview)
        self.scroll_bar.lift(self.canv_subframe)
        label.lift()

    def resize_window(self, event):
        """On resize of canvas, ensure subframe matches width."""
        self.canv.itemconfigure("my_frame", width=event.width)
        self.canv_subframe.configure(
            width=event.width
        )  # self.canv.winfo_width()

    def process_items(self, items: pd.DataFrame) -> pd.DataFrame:
        """
        Need to translate cols to tkinter variables.
        """
        if items is None:
            return items

        item_var_map = {
            "ENTRY": tk.StringVar,
            "DROPDOWN": tk.IntVar,
            "BOOLEAN": tk.BooleanVar,
            "NUM_ENTRY": tk.StringVar,
        }

        def valid_check(data_type, val):
            """ If data type is invalid for var type, load empty variable."""
            if data_type in ["DROPDOWN", "BOOLEAN"]:
                if isinstance(val, (bool, int, np.int64, np.int32)):
                    return True
                return False
            if data_type in ["NUM_ENTRY"]:
                if isinstance(val, (float, int, np.int64, np.int32, np.float32, np.float64)) and not np.isnan(val):
                    return True
                return False

            if data_type in ["ENTRY"] and isinstance(val, (float, int, np.int64, np.int32, np.float32, np.float64)):
                return False
            return True

        return pd.DataFrame([
            [
                item[c] if c not in self.item_map.keys(
                ) else (
                    item_var_map[self.item_map[c]](value=item[c])
                    if valid_check(self.item_map[c], item[c])
                    else item_var_map[self.item_map[c]](value=None)
                )
                for c in items.columns
            ]
            for _, item in items.iterrows()
        ], columns=items.columns, index=items.index)

    def add_item(self) -> None:
        """ Note: Button next to label to add an item."""
        new_item = []
        item_var_map = {
            "ENTRY": tk.StringVar,
            "DROPDOWN": tk.IntVar,
            "BOOLEAN": tk.BooleanVar,
            "NUM_ENTRY": tk.StringVar,
        }

        for col in self.items.columns:
            if col not in self.item_map:
                new_item += [None]  # e.g. id (generated later)
            else:
                new_item += [item_var_map[self.item_map[col]]()]

        # Add item to items, and update visuals.
        self.items = self.items.append(
            pd.Series(new_item, index=self.items.columns),
            ignore_index=True
        )

        self.update_list()

    def delete_item(self, item_index: int) -> None:
        """
        Save altered list, Delete item from items, and update canvas
        """
        logger.debug("Deleting: %d", item_index)
        self.items = self.items.drop(index=item_index)

        self.update_list()

    def get_items(self) -> pd.DataFrame:
        """ Items Pandas DataFrame need to transform variables back to raw values."""
        # TODO: Perform data validity checks based on entry type
        return pd.DataFrame([
            [
                item[col] if col not in self.item_map.keys() else item[col].get()
                for col in self.items.columns
            ]
            for _, item in self.items.iterrows()
        ], columns=self.items.columns, index=self.items.index)

    def update_list(self) -> None:
        """ Remove all widgets from subframe, then reload """
        # Delete items in canvas
        for widgets in self.canv_subframe.winfo_children():
            widgets.destroy()

        # There are no items
        if self.items is None:
            return

        # Load up all items into canvas
        for idx, item in self.items.iterrows():
            item_frame = tk.Frame(self.canv_subframe,
                                  borderwidth=1, width=self.canv_width)

            IMG_HEIGHT = 10
            btn = tk.Button(
                item_frame,
                text="Remove",
                compound=tk.RIGHT,
                command=partial(self.delete_item, item_index=idx),
                # image=ImageTk.PhotoImage(
                #     BIN_IMG.resize(
                #         (int(IMG_HEIGHT / BIN_IMG.size[1]*BIN_IMG.size[0]), int(IMG_HEIGHT)))
                # ),
                # padx=2, pady=2
            )
            btn.pack(side=tk.TOP, anchor="e", padx=(5, 0))

            for col, entry_type in self.item_map.items():
                if entry_type == "BOOLEAN":
                    tk.Checkbutton(
                        item_frame, text=col, variable=item[col]
                    ).pack(side=tk.TOP, anchor="w", padx=(0, 5))

                if entry_type in ["ENTRY", "NUM_ENTRY"]:
                    entry_frame = tk.Frame(item_frame, width=self.canv_width)
                    tk.Label(entry_frame, text=col).pack(
                        side="left", padx=(0, 5))
                    tk.Entry(entry_frame, textvariable=item[col]).pack(
                        side="right", fill=tk.X, expand=True
                    )
                    entry_frame.pack(
                        side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5)
                    )

                if entry_type == "DROPDOWN":
                    MenuSingleSelector(
                        item_frame, col, self.options[col], var=item[col]
                    ).pack(side=tk.TOP, anchor="w", padx=(0, 5))

            item_frame.pack(
                side="top", fill=tk.X, expand=True, pady=10
            )
            item_frame.config(highlightbackground="black",
                              highlightcolor="red", highlightthickness=2)

        # Resize canvas scrollable window
        self.update_idletasks()
        self.canv.config(
            scrollregion=(
                0, 0,
                self.canv_width,
                self.canv_subframe.winfo_height()
            )
        )
