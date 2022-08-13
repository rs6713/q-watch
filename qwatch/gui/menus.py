import logging
from typing import Dict, List

import pandas as pd
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class MenuSingleSelector(ttk.Menubutton):
    def __init__(self, parent: ttk.Frame, name: str, options: pd.DataFrame, default: int = None, var: tk.Variable = None, **kwargs):
        ttk.Menubutton.__init__(
            self,
            parent,
            text=name,
            # relief=tk.RAISED,
            **kwargs
        )
        menu = tk.Menu(self, tearoff=0)
        self["menu"] = menu
        self.configure(menu=menu)
        self.menu = menu
        self.labels = {}

        # Variable can be passed in from external
        if var is None:
            self.selected_variable = tk.IntVar()
        else:
            self.selected_variable = var

        for _, option in options.iterrows():
            label = f"{option.LABEL} - {option.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in option.index else option.LABEL

            self.labels[option.ID] = label

            self.menu.add_radiobutton(
                label=label,
                value=option.ID,
                variable=self.selected_variable,
                command=self.set_menu_label
            )

        if default is not None:
            self.selected_variable.set(default)

        if self.selected_variable.get() and self.selected_variable.get() != -1:
            self.set_menu_label()

    def set_menu_label(self):
        self.configure(text=self.labels[self.selected_variable.get()])

    def get_selected_option(self):
        if self.selected_variable.get() in self.labels.keys():
            return self.selected_variable.get()
        else:
            return None


class MenuMultiSelector(ttk.Menubutton):
    def __init__(self, parent, name, options, default: List[int] = None, descrip_var=None, **kwargs):
        ttk.Menubutton.__init__(
            self,
            parent,
            text=name,
            # relief=tk.RAISED,
            **kwargs
        )
        menu = tk.Menu(self, tearoff=0)
        self["menu"] = menu
        self.configure(menu=menu)
        self.menu = menu

        def get_label(option):
            return f"{option.LABEL} - {option.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in option.index else option.LABEL

        def update_description():
            if descrip_var is not None:

                labels = [
                    get_label(options.set_index("ID").loc[option_id])
                    for option_id, checked in self.options.items()
                    if checked.get()
                ]
                descrip_var.set(
                    "(" + ", ".join(labels) + ")"
                )

        self.options = {}
        for _, option in options.iterrows():
            var = tk.IntVar(value=0) if (
                default is None or option.ID not in default) else tk.IntVar(value=1)

            self.menu.add_checkbutton(label=get_label(
                option), variable=var, command=update_description)
            self.options[option.ID] = var

    def get_selected_options(self):

        return [
            option_id for option_id, checked in self.options.items()
            if checked.get()
        ]


class ChecklistBox(tk.Frame):
    def __init__(self, parent, name, choices, radio: str = None, height=100, width=110, id_name=None, **kwargs):
        """
        List of checked options

        Params
        ------
        radio: str
            Additional check
        """
        tk.Frame.__init__(self, parent)

        self.name = name
        self.radio = radio
        self.id_name = id_name

        label = ttk.Label(self, text=name)
        label.pack(side="top", fill=tk.X, pady=(0, 5))

        scroll_bar = ttk.Scrollbar(self)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # creating a canvas
        canv = tk.Canvas(self)
        canv.config(relief='flat', width=width, height=height, bd=2)
        # placing a canvas into frame
        #self.canv.grid(column = 0, row = 0, sticky = 'nsew')
        canv.pack(side="left", fill=tk.Y)

        subFrame = ttk.Frame(self)  # relief=tk.GROOVE, bd=1

        self.vars = {}
        self.radio_vars = {}
        bg = self.cget("background")
        for i, choice in choices.iterrows():
            var = tk.IntVar()
            radio_var = tk.IntVar(value=1)
            self.vars[choice.ID] = var

            ttk.Checkbutton(
                subFrame,
                var=var,
                text=choice.LABEL,
                onvalue=1, offvalue=0,
                width=20,
            ).pack(side="top", fill="both", anchor="w", expand=True)
            if self.radio is not None:
                self.radio_vars[choice.ID] = radio_var

                ttk.Checkbutton(
                    subFrame,
                    var=radio_var,
                    text=radio,
                    onvalue=1, offvalue=0,
                    width=20,
                ).pack(side="top", fill="both", anchor="w", expand=True, padx=(10, 0))

        canv.create_window(0, 0, window=subFrame, anchor='nw')
        parent.update_idletasks()

        canv.config(
            yscrollcommand=scroll_bar.set,
            scrollregion=(0, 0, width, subFrame.winfo_height())  # bbox#
        )
        scroll_bar.config(command=canv.yview)
        scroll_bar.lift(subFrame)
        label.lift()

        def _on_mousewheel(event):
            canv.yview_scroll(int(-1*(event.delta/120)), "units")
        # Configure canv with scroll wheel
        self.bind('<Enter>', lambda _: canv.bind_all(
            "<MouseWheel>", _on_mousewheel))
        self.bind('<Leave>', lambda _: canv.unbind_all("<MouseWheel>"))

    def get_selected_options(self):
        ids = []
        for idd, checked in self.vars.items():
            if checked.get():
                d = {
                    self.id_name: idd,
                    **({} if self.radio is None else {self.radio: self.radio_vars[idd].get()})
                }
                ids.append(d)
        return ids

    def load(self, ids: pd.DataFrame = None):
        # Refresh checklist
        if ids is None:
            for idd in self.vars.keys():
                self.vars[idd].set(0)
            return

        for idd in ids.ID.values:
            if idd in self.vars.keys():
                self.vars[idd].set(1)
            else:
                logger.warning(
                    f"Item {idd} does not exist in {self.name} Checklistbox"
                )
            if self.radio is not None:
                if idd in self.radio_vars.keys():
                    self.radio_vars[idd].set(
                        ids[ids.ID == idd].iloc[0, :][self.radio]
                    )
