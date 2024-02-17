import os
import requests


def streamable_upload(self, file_path) -> str:
    file_processed = {
        "file": (file_path.split("/")[-1], open(f"app/{file_path}", "rb")),
    }
    email = os.environ.get("STREAMABLE_LOGIN") or ""
    password = os.environ.get("STREAMABLE_PASSWORD") or ""
    try:
        response = requests.post(
            "https://api.streamable.com/upload",
            auth=(email, password),
            files=file_processed,
        ).json()
        return response
    except Exception as e:
        raise Exception(f"Problem uploading to streamable: {e}")
