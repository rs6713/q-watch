from io import BytesIO

import pandas as pd
from PIL import Image


def get_first_name(name: str):

    if len(name.split(" ")) == 1:
        return name

    return " ".join(name.split(" ")[:-1])


def get_last_name(name: str):

    if len(name.split(" ")) == 1:
        return ""

    return name.split(" ")[-1]


def describe_obj(obj):
    description = ""
    for k in obj.keys():
        if isinstance(obj[k], str):
            description += f"{k}: {obj[k][:40]}{'...' if len(obj[k]) > 40 else ''}"
        elif isinstance(obj[k], pd.DataFrame):
            description += f"{k}: {obj[k].shape}: {','.join(obj[k].columns)}"
        elif isinstance(obj[k], (int, float)):
            description += f"{k}: {obj[k]}"
        elif isinstance(obj[k], dict):
            description += f"{k}: {', '.join(obj[k].keys())}"
        else:
            description += f"{k}:"
        description += "\n"

    return description
