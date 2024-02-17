from pathlib import Path
import os

MEDIA_DIR_PATH: Path = Path("app/static/media")
IMAGES_DIR_PATH: Path = MEDIA_DIR_PATH / "images"
VIDEOS_DIR_PATH: Path = MEDIA_DIR_PATH / "videos"

PLEX_TOKEN = os.environ.get("PLEX_TOKEN")
PLEX_URL = os.environ.get("PLEX_URL")