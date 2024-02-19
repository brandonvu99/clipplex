from pathlib import Path
import os

GENERATED_MEDIA_DIRPATH: Path = Path("./clipplex/static/generated_media")
IMAGES_DIRPATH: Path = GENERATED_MEDIA_DIRPATH / "images"
CLIPS_DIRPATH: Path = GENERATED_MEDIA_DIRPATH / "clips"
IMAGES_DIRPATH.mkdir(parents=True, exist_ok=True)
CLIPS_DIRPATH.mkdir(parents=True, exist_ok=True)

PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH: dict[Path, Path] = {
    Path(r"E:/Media/") : Path(r"../Media")
}

PLEX_TOKEN = os.environ.get("PLEX_TOKEN")
PLEX_URL = os.environ.get("PLEX_URL")