from clipplex.config import (
    IMAGES_DIRPATH,
    CLIPS_DIRPATH,
    PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH,
)
from clipplex.models.image import Image
from clipplex.models.clip import Clip_
from pathlib import Path
import ffmpeg
import os


def delete_file(self, file_path) -> bool:
    try:
        os.remove(f"./app/{file_path}")
        return True
    except:
        return False
