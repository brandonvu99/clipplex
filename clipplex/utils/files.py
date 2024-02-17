from clipplex.config import IMAGES_DIR_PATH, VIDEO_DIR_PATH
from clipplex.models.image import Image
from clipplex.models.video import Video_
from pathlib import Path
import ffmpeg
import os


def get_images() -> list[str]:
    return [
        Image(Path(dirpath) / filename).filepath
        for dirpath, _, filenames in os.walk(IMAGES_DIR_PATH)
        for filename in filenames
    ]


def get_instant_videos() -> list[dict[str, str]]:
    return [
        Video_.from_filepath(Path(dirpath) / filename).to_dict()
        for dirpath, _, filenames in os.walk(VIDEO_DIR_PATH)
        for filename in filenames
    ]


def delete_file(self, file_path) -> bool:
    try:
        os.remove(f"./app/{file_path}")
        return True
    except:
        return False
