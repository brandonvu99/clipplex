from clipplex.config import MEDIA_PATH, VIDEO_DIR_PATH
from clipplex.models.video import Video_
from pathlib import Path
import ffmpeg
import os


def get_images_in_folder() -> list:
    folder = os.path.join(MEDIA_PATH, "images")
    folder_list = []
    for a in os.listdir(folder):
        a = f"{folder}/{a}"
        folder_list.append(
            f"{a.split('/')[-4]}/{a.split('/')[-3]}/{a.split('/')[-2]}/{a.split('/')[-1]}"
        )
    return sorted(folder_list)


def get_instant_videos() -> list:
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
