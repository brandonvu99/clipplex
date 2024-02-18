from clipplex.config import IMAGES_DIRPATH
from pathlib import Path
import os

class Image(object):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
    
    @staticmethod
    def get_all_images() -> list[str]:
        return [
            Image(Path(dirpath) / filename).filepath
            for dirpath, _, filenames in os.walk(IMAGES_DIRPATH)
            for filename in filenames
        ]
