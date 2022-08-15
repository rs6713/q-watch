from functools import partial
import logging
import pathlib
import os
from typing import List
import uuid

import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

from qwatch.gui.menus import MenuSingleSelector


BIN_IMG = Image.open(os.path.join(
    pathlib.Path(__file__).parent.parent,
    "static", "icons", "bin.png"
))

logger = logging.getLogger(__name__)


def get_options(df_in: pd.DataFrame, id_col: str, label_cols: List[str], sep: str = " ") -> pd.DataFrame:
    if df_in.empty:
        return pd.DataFrame([], columns=[id_col, *label_cols])

    df = df_in.copy()
    df.loc[:, "LABEL"] = df.apply(
        lambda row: sep.join([str(row[c]) for c in label_cols]),
        axis=1
    )
    df.rename(columns={id_col: "ID"}, inplace=True)
    return df.loc[:, ["LABEL", "ID"]]


class TextExtension(ttk.Frame):
    """Extends Frame.  Intended as a container for a Text field.  Better related data handling
    and has Y scrollbar."""

    def __init__(self, parent, textvariable=None, *args, **kwargs):

        super(TextExtension, self).__init__(parent)

        self._y_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)

        self._text_widget = tk.Text(
            self, yscrollcommand=self._y_scrollbar.set, *args, **kwargs)
        self._text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self._y_scrollbar.config(command=self._text_widget.yview)
        self._y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Fill widget with contents of var
        # Setup trace, so when text modified, var is updated.
        if textvariable is not None:
            if not (isinstance(textvariable, tk.Variable)):
                raise TypeError("tkinter.Variable type expected, " +
                                str(type(textvariable)) + " given.".format(type(textvariable)))
            self._text_variable = textvariable
            self.var_modified()
            self._text_trace = self._text_widget.bind(
                '<<Modified>>', self.text_modified)
            self._var_trace = textvariable.trace("w", self.var_modified)

    def text_modified(self, *args):
        """If variable exists, update text variable."""
        if self._text_variable is not None:
            # Delete trace, to stop looping, by updating text, as var updated
            self._text_variable.trace_vdelete("w", self._var_trace)
            self._text_variable.set(self._text_widget.get(1.0, tk.END))
            self._var_trace = self._text_variable.trace(
                "w", self.var_modified)
            self._text_widget.edit_modified(False)

    def var_modified(self, *args):
        """Update text when contents of variable changes."""
        self.set_text(self._text_variable.get())
        self._text_widget.edit_modified(False)

    # def unhook(self):
    #     if self._text_variable is not None:
    #         self._text_variable.trace_vdelete("w", self._var_trace)

    def set_text(self, _value):
        self._text_widget.delete("1.0", tk.END)
        if (_value is not None):
            self._text_widget.insert(tk.END, _value)


class EditableList(ttk.Frame):
    def __init__(self, parent: tk.Frame, name: str, items: pd.DataFrame = None, item_map: dict = None, options: dict = None, group: str = None):
        """
        Editable List - With deletable and editable items

        group - editable items are grouped into cohesive groups this way
        """
        ttk.Frame.__init__(
            self, parent,   # height=height  # , width=width, height=height,
        )

        self.name = name
        self.item_map = item_map
        self.options = options
        self.group = group

        self.items = self.process_items(items)

        label_frame = ttk.Frame(self)
        label = ttk.Label(label_frame, text=name)
        label.pack(side="left", fill=tk.X, expand=True)

        ttk.Button(
            label_frame, text="New",
            command=self.add_item,  # , padx=5, pady=2
            style='Accent.TButton'
        ).pack(side="right")
        label_frame.pack(side="top", fill=tk.X, pady=(0, 5))

        ################################################
        # Quotes Subframe
        # Canvas with scroll, place subframe inside canvas
        ################################################
        self.scroll_bar = ttk.Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # creating a canvas
        self.canv = tk.Canvas(self)  # , width=self.canv_width
        # self.canv.config(relief='flat', bd=2)  # width=self.canv_width
        self.canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, padx=(0, 5))

        # self.canvas = Canvas(self, width = self.app_sizex, height = self.app_sizey, scrollregion=(0,0,x,y))

        # Will contain quotes
        self.canv_subframe = tk.Frame(self.canv)  # , width=self.canv_width

        # Load original quotes list
        self.update_list()

        self.canv.create_window(
            (0, 0), window=self.canv_subframe, anchor="nw", tags='my_frame')
        self.canv.bind('<Configure>', self.resize_window)
        parent.update_idletasks()  # So winfo_height dimensions are accurate

        self.canv.config(
            yscrollcommand=self.scroll_bar.set,
            scrollregion=(0, 0, self.canv_subframe.winfo_width(),  # self.canv_width,
                          self.canv_subframe.winfo_height())
        )

        self.scroll_bar.config(command=self.canv.yview)
        self.scroll_bar.lift(self.canv_subframe)
        label.lift()

        # Scrollwheel handling
        def _on_mousewheel(event):
            self.canv.yview_scroll(int(-1*(event.delta/120)), "units")
        # Configure canv with scroll wheel
        self.bind('<Enter>', lambda _: self.canv.bind_all(
            "<MouseWheel>", _on_mousewheel))
        self.bind('<Leave>', lambda _: self.canv.unbind_all("<MouseWheel>"))

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

        logger.debug("Procesing in EditableList %s items %s", self.name, items)
        item_var_map = {
            "ENTRY": tk.StringVar,
            "DROPDOWN": tk.IntVar,
            "BOOLEAN": tk.BooleanVar,
            "NUM_ENTRY": tk.StringVar,
        }

        def valid_check(data_type: str, val):
            """ If data type is invalid for var type, load empty variable."""
            if data_type in ["DROPDOWN", "BOOLEAN"]:
                if isinstance(val, (bool, int, np.int64, np.int32)):
                    return True
                logger.debug(
                    "VALID_CHECK value %s for %s is invalid", str(val), data_type)
                return False
            if data_type in ["NUM_ENTRY"]:
                if isinstance(val, (float, int, np.int64, np.int32, np.float32, np.float64)) and not np.isnan(val):
                    return True
                return False

            if data_type in ["ENTRY"] and isinstance(val, (float, int, np.int64, np.int32, np.float32, np.float64)):
                return False
            return True

        items = pd.DataFrame([
            [
                item[c] if c not in self.item_map.keys(
                ) else (
                    item_var_map[self.item_map[c]](value=item[c])
                    if valid_check(self.item_map[c], item[c])
                    else item_var_map[self.item_map[c]](value=None)
                )
                for c in items.columns
            ]
            for item in items.to_dict("records")
        ], columns=items.columns, index=items.index)

        logger.debug("EditableList Processed items: %s", items)
        return items

    def add_item(self, group=None) -> None:
        """ Note: Button next to label to add an item."""
        new_item = []
        item_var_map = {
            "ENTRY": tk.StringVar,
            "DROPDOWN": tk.IntVar,
            "BOOLEAN": tk.BooleanVar,
            "NUM_ENTRY": tk.StringVar,
        }

        for col in self.item_map.keys():
            new_item += [item_var_map[self.item_map[col]]()]

        # Add item to items, and update visuals.
        if self.items is None:
            if self.group is not None:
                new_id = uuid.uuid4().int & (1 << 64)-1
                self.items = pd.DataFrame(
                    [[*new_item, (group or new_id)]],
                    columns=[*list(self.item_map.keys()), self.group]
                )
            else:
                self.items = pd.DataFrame(
                    [new_item], columns=list(self.item_map.keys()))
        else:
            if self.group is not None:
                new_id = uuid.uuid4().int & (1 << 64)-1
                self.items = self.items.append(
                    pd.Series(
                        [*new_item, (group or new_id)],
                        index=[*list(self.item_map.keys()), self.group]
                    ),
                    ignore_index=True
                )
            else:
                self.items = self.items.append(
                    pd.Series(new_item, index=list(self.item_map.keys())),
                    ignore_index=True
                )
        self.update_list()

    def delete_item(self, item_index: int = None, group=None) -> None:
        """
        Save altered list, Delete item from items, and update canvas
        """
        if item_index is None and group is None:
            logger.warning(
                "Cannot delete unspecified item"
            )
            return

        if group is not None:
            logger.debug("Deleting item group: %s", str(group))
            self.items = self.items[
                self.items[self.group] != group
            ]
        else:
            logger.debug("Deleting: %d", item_index)
            self.items = self.items.drop(index=item_index)

        self.update_list()

    def get_items(self) -> pd.DataFrame:
        """ Items Pandas DataFrame need to transform variables back to raw values."""
        if self.items is None:
            return None

        # TODO: Perform data validity checks based on entry type
        return pd.DataFrame([
            [
                item[col] if col not in self.item_map.keys() else item[col].get()
                for col in self.items.columns
            ]
            for _, item in self.items.iterrows()
        ], columns=self.items.columns, index=self.items.index)

    def load(self, items: pd.DataFrame = None, options=None) -> None:
        if options is not None:
            self.options = options
        if items is not None:
            self.items = self.process_items(items)
        self.update_list()

    def update_list(self) -> None:
        """ Remove all widgets from subframe, then reload """
        # Delete items in canvas
        for widgets in self.canv_subframe.winfo_children():
            widgets.destroy()

        # There are no items
        if self.items is None or self.items.empty:
            return

        items = self.items.copy()
        if self.group is None:
            items.loc[:, "GROUPING_COL"] = "GROUP"

        # Load up all items into canvas
        for grp, item_group in items.groupby(self.group or "GROUPING_COL"):
            group_frame = ttk.Frame(
                self.canv_subframe, style="Card.TFrame"
            )
            if self.group is not None:

                command_frame = ttk.Frame(group_frame)
                ttk.Button(
                    command_frame,
                    text="New",
                    compound=tk.RIGHT,
                    command=partial(
                        self.add_item, group=grp)
                ).pack(side="right")
                ttk.Button(
                    command_frame,
                    text="Remove",
                    compound=tk.RIGHT,
                    command=partial(self.delete_item, group=grp)
                ).pack(side="right", padx=(0, 5))
                command_frame.pack(side="top", anchor="e")

            for idx, item in item_group.iterrows():
                item_frame = ttk.Frame(
                    group_frame
                    # self.canv_subframe,
                    # width=self.canv_width,
                    # style='Card.TFrame',
                )

                ttk.Button(
                    item_frame,
                    text="Remove",
                    compound=tk.RIGHT,
                    command=partial(self.delete_item, item_index=idx),
                    # image=ImageTk.PhotoImage(
                    #     BIN_IMG.resize(
                    #         (int(IMG_HEIGHT / BIN_IMG.size[1]*BIN_IMG.size[0]), int(IMG_HEIGHT)))
                    # ),
                    # padx=2, pady=2
                ).pack(side=tk.TOP, anchor="e", padx=5, pady=5)

                for col, entry_type in self.item_map.items():
                    if entry_type == "BOOLEAN":
                        ttk.Checkbutton(
                            item_frame, text=col, variable=item[col],
                            style='Switch.TCheckbutton'
                        ).pack(side=tk.TOP, anchor="w", padx=5, pady=(0, 5))

                    if entry_type in ["ENTRY", "NUM_ENTRY"]:
                        entry_frame = ttk.Frame(item_frame)
                        ttk.Label(entry_frame, text=col).pack(
                            side="left", padx=(0, 5))
                        ttk.Entry(entry_frame, textvariable=item[col]).pack(
                            side="right", fill=tk.X, expand=True
                        )
                        entry_frame.pack(
                            side=tk.TOP, expand=1, fill=tk.X, pady=(0, 5), padx=5
                        )

                    if entry_type == "DROPDOWN":
                        MenuSingleSelector(
                            item_frame, col, self.options[col], var=item[col]
                        ).pack(side=tk.TOP, anchor="w", padx=5, pady=(0, 5))

                item_frame.pack(
                    side="top", fill=tk.X, expand=True, pady=2
                )
                # item_frame.config(highlightbackground="black",
                #                   highlightcolor="red", highlightthickness=2)
            group_frame.pack(
                side="top", fill=tk.X, expand=True, pady=10
            )
        # Resize canvas scrollable window
        self.update_idletasks()
        self.canv.config(
            scrollregion=(
                0, 0,
                self.canv_subframe.winfo_width(),
                self.canv_subframe.winfo_height()
            )
        )
