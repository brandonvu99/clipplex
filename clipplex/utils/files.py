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


def plex_filepath_to_clipplex_filepath(plex_filepath: Path) -> Path:
    """
    Converts a given plex filepath to its respective clipplex filepath based off of the mapping {PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH}.
    The most specific (or lowest common ancestor) of all {PLEX_DIRPATH}s for the given plex filepath is chosen. For example, for the following mapping:

    PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH = {
        "/long/plex/path/to/media/" : "/clipplex/Media/",
        "/long/plex/path/to/media/but/more/specific/" : "/clipplex/other/media/dir/",
    }

    a plex filepath of "/long/plex/path/to/media/but/more/specific/Drag Race/s01e01.mkv" will be mapped to "/clipplex/other/media/dir/Drag Race/s01e01.mkv"
    because even though "/long/plex/path/to/media/" COULD match, the more specific one matches.
    """

    plex_dirpath_ancestors = [
        plex_dirpath
        for plex_dirpath in PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH.keys()
        if plex_filepath.is_relative_to(plex_dirpath)
    ]
    if not plex_dirpath_ancestors:
        raise ValueError(
            f"The given plex_filepath ({plex_filepath}) does not have an associated mapping in PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH."
        )
    most_specific_plex_dir = Path(os.path.commonpath(plex_dirpath_ancestors))

    clipplex_dirpath = PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH[most_specific_plex_dir]
    relative_filepath = plex_filepath.relative_to(most_specific_plex_dir)

    return clipplex_dirpath / relative_filepath

