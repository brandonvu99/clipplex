from clipplex import flaskapp
import logging

def main():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
        level=logging.NOTSET,
        handlers=[
            logging.FileHandler(filename="./logs/clipplex.log", encoding="utf-16"),
            logging.StreamHandler(),
        ],
    )

if __name__ == '__main__':
    main()
