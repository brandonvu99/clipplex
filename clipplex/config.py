from pathlib import Path
import os

MEDIA_DIRPATH: Path = Path("app/static/media")
IMAGES_DIRPATH: Path = MEDIA_DIRPATH / "images"
VIDEOS_DIRPATH: Path = MEDIA_DIRPATH / "videos"

PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH: dict[Path, Path] = {
    Path(r"E:/Media/") : Path(r"/Media")
}

PLEX_TOKEN = os.environ.get("PLEX_TOKEN")
PLEX_URL = os.environ.get("PLEX_URL")