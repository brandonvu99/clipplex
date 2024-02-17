from pathlib import Path

class Image(object):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath