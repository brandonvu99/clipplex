from clipplex.config import (
    IMAGES_DIR_PATH,
    VIDEOS_DIR_PATH,
    PLEX_DIR_PATH_TO_CLIPPLEX_DIR_PATH,
)
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
        for dirpath, _, filenames in os.walk(VIDEOS_DIR_PATH)
        for filename in filenames
    ]


def delete_file(self, file_path) -> bool:
    try:
        os.remove(f"./app/{file_path}")
        return True
    except:
        return False


def plex_filepath_to_clipplex_filepath(plex_filepath: Path) -> Path:
    """
    Converts a given plex filepath to its respective clipplex filepath based off of the mapping {PLEX_DIR_PATH_TO_CLIPPLEX_DIR_PATH}.
    The most specific (or lowest common ancestor) of all {PLEX_DIR_PATH}s for the given plex filepath is chosen. For example, for the following mapping:

    PLEX_DIR_PATH_TO_CLIPPLEX_DIR_PATH = {
        "/long/plex/path/to/media/" : "/clipplex/Media/",
        "/long/plex/path/to/media/but/more/specific/" : "/clipplex/other/media/dir/",
    }

    a plex filepath of "/long/plex/path/to/media/but/more/specific/Drag Race/s01e01.mkv" will be mapped to "/clipplex/other/media/dir/Drag Race/s01e01.mkv"
    because even though "/long/plex/path/to/media/" COULD match, the more specific one matches.
    """

    plex_dir_path_ancestors = [
        plex_dir_path
        for plex_dir_path in PLEX_DIR_PATH_TO_CLIPPLEX_DIR_PATH.keys()
        if plex_filepath.is_relative_to(plex_dir_path)
    ]
    if not plex_dir_path_ancestors:
        raise ValueError(
            f"The given plex_filepath ({plex_filepath}) does not have an associated mapping in PLEX_DIR_PATH_TO_CLIPPLEX_DIR_PATH."
        )
    most_specific_plex_dir = Path(os.path.commonpath(plex_dir_path_ancestors))

    clipplex_dir_path = PLEX_DIR_PATH_TO_CLIPPLEX_DIR_PATH[most_specific_plex_dir]
    relative_filepath = plex_filepath.relative_to(most_specific_plex_dir)

    return clipplex_dir_path / relative_filepath

