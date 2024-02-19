import logging
from pathlib import Path
LOG_DIRPATH = Path("../logs")
LOG_DIRPATH.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    level=logging.NOTSET,
    handlers=[
        logging.FileHandler(filename=LOG_DIRPATH / "clipplex.log", encoding="utf-16"),
        logging.StreamHandler(),
    ],
)

from clipplex import flaskapp