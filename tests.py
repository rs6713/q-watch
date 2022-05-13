# %%
from functools import partial
import pathlib
import os

import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk

from IPython.display import display


BIN_IMG = Image.open(os.path.join(
    pathlib.Path(__file__).parent,
    "qwatch", "static", "icons", "bin.png"
))
sz = 20
display(BIN_IMG.resize((sz, sz)))
# %%
