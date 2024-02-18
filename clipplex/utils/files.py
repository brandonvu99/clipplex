import os


def delete_file(file_path) -> bool:
    try:
        os.remove(f"./app/{file_path}")
        return True
    except:
        return False
