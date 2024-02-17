from clipplex.config import MEDIA_PATH
import subprocess


class Snapshot:
    def __init__(self, media_path: str, time: str, fps: float):
        self.media_path = media_path
        self.time = time
        self.fps = int(fps)

    def _download_frames(self):
        cmd = f"ffmpeg -ss {self.time} -i {self.media_path} -vframes {self.fps} -qscale:v 2 {MEDIA_PATH}/images/{self.time.replace(':','_')}_%03d.jpg"
        a = subprocess.call(
            cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )
