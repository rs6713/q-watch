from pathlib import Path
import os

print(Path(__file__).parent)
for name in os.listdir(
    os.path.join(
        Path(__file__).parent,
        "website", "src", "static", "movie-pictures"
    )
):
    print(name)
    new_name = name.split(".", 1)[0] + ".jpg"
    print(new_name)
    os.rename(
        os.path.join(
            Path(__file__).parent,
            "website", "src", "static", "movie-pictures", name
        ),
        os.path.join(
            Path(__file__).parent,
            "website", "src", "static", "movie-pictures", new_name
        )
    )
