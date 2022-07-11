from io import BytesIO


from PIL import Image


def get_first_name(name: str):

    if len(name.split(" ")) == 1:
        return name

    return " ".join(name.split(" ")[:-1])


def get_last_name(name: str):

    if len(name.split(" ")) == 1:
        return ""

    return name.split(" ")[-1]
