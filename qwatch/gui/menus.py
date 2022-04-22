import tkinter as tk


class MenuMultiSelector(tk.Menubutton):
  def __init__(self, parent, name, options, **kwargs):
    tk.Menubutton.__init__(
      self,
      parent,
      text=name,
      relief=tk.RAISED,
      **kwargs
    )
    menu = tk.Menu(self, tearoff=0)
    self["menu"] = menu
    self.configure(menu=menu)
    self.menu = menu

    self.options = {}
    for _, option in options.iterrows():
        var = tk.IntVar()
        label = f"{option.LABEL} - {option.SUB_LABEL or 'NULL'}" if "SUB_LABEL" in option.index else option.LABEL
        self.menu.add_checkbutton(label=label, variable=var)
        options[option.ID] = var

  def get_selected_options(self):

    return [
      option_id for option_id, checked in self.options.items()
      if checked.get()
    ]

class ChecklistBox(tk.Frame):
  def __init__(self, parent, name, choices, height=100, width=150, **kwargs):
    tk.Frame.__init__(self, parent)

    label = tk.Label(self, text=name)
    label.pack(side="top", fill=tk.X)

    scroll_bar = tk.Scrollbar(self)
    scroll_bar.pack(side=tk.RIGHT, fill = tk.Y)

    # creating a canvas
    canv = tk.Canvas(self)
    canv.config(relief = 'flat', width=width, height=height, bd = 2)
    # placing a canvas into frame
    #self.canv.grid(column = 0, row = 0, sticky = 'nsew')
    canv.pack(side="left", fill=tk.Y)

    subFrame = tk.Frame(self)#relief=tk.GROOVE, bd=1

    self.vars = {}
    bg = self.cget("background")
    for i, choice in choices.iterrows():
      var = tk.IntVar()
      self.vars[choice.ID] = var
      cb = tk.Checkbutton(subFrame, var=var, text=choice.LABEL,
                          onvalue=1, offvalue=0,
                          anchor="w", width=20, background=bg,
                          relief="flat", highlightthickness=0
      )
      cb.pack(side="top", fill="both", anchor="w", expand=True)
    

    #subFrame.pack(side="left", fill="both", expand=True)
    #subFrame.pack_propagate(0)
    canv.create_window(0, 0, window = subFrame, anchor = 'nw')
    parent.update_idletasks() 
    bbox = canv.bbox("all")
    #print(bbox, subFrame.bbox("all"), subFrame.winfo_height() )
    canv.config(
      yscrollcommand = scroll_bar.set,
      scrollregion = (0, 0, width, subFrame.winfo_height()) #bbox#
    )
    scroll_bar.config(command=canv.yview)
    scroll_bar.lift(subFrame) 
    label.lift()

  def get_selected_options(self):
    ids = []
    for idd, checked  in self.vars.items():
      value =  checked.get()
      if value:
        ids.append(idd)
    return ids
