import logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    level=logging.NOTSET,
    handlers=[
        logging.FileHandler(filename="../logs/clipplex.log", encoding="utf-16"),
        logging.StreamHandler(),
    ],
)

from clipplex import flaskapp