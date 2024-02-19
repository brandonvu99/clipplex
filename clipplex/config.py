from pathlib import Path, PurePath, PureWindowsPath
import os
import yaml

GENERATED_MEDIA_DIRPATH: Path = Path("./clipplex/static/generated_media")
IMAGES_DIRPATH: Path = GENERATED_MEDIA_DIRPATH / "images"
CLIPS_DIRPATH: Path = GENERATED_MEDIA_DIRPATH / "clips"
IMAGES_DIRPATH.mkdir(parents=True, exist_ok=True)
CLIPS_DIRPATH.mkdir(parents=True, exist_ok=True)

CONFIG_DEFAULT: dict = {"PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH": {}}
CONFIG_DIRPATH: Path = Path("./config/")
CONFIG_DIRPATH.mkdir(parents=True, exist_ok=True)
CONFIG_FILEPATH: Path = CONFIG_DIRPATH / "config.yaml"
if not CONFIG_FILEPATH.exists():
    with open(CONFIG_FILEPATH, "w") as f:
        yaml.dump(CONFIG_DEFAULT, f)
with open(CONFIG_FILEPATH, "r") as f:
    config = yaml.safe_load(f)
PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH: dict[Path, Path] = {
    PurePath(PureWindowsPath(plex_dirpath).as_posix()): PurePath(
        PureWindowsPath(clipplex_dirpath).as_posix()
    )
    for plex_dirpath, clipplex_dirpath in config[
        "PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH"
    ].items()
}

PLEX_TOKEN = os.environ.get("PLEX_TOKEN")
PLEX_URL = os.environ.get("PLEX_URL")
