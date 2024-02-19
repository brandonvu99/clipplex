from __future__ import annotations
from datetime import timedelta, datetime
from clipplex.config import CLIPS_DIRPATH
from clipplex.models.plex import ActivePlexInfo
from clipplex.utils.timing import timestamp_str_of
from pathlib import Path
import ffmpeg
import logging
import os
import time


class Clip:
    def __init__(
        self, plex_info: ActivePlexInfo, start_time: timedelta, end_time: timedelta
    ):
        self.media_path = plex_info.media_path
        self.start_time = start_time
        self.end_time = end_time

        self.metadata = {
            "title": plex_info.media_title,
            "show": plex_info.show_name,
            "season": plex_info.season,
            "episode": plex_info.episode_number,
            "episode_timestamp": plex_info.current_media_time_str,
            "artist": plex_info.username,
        }

        media_filepath_relative = self.media_path.relative_to("../Media")
        media_file_extension = self.media_path.suffix
        self.save_filepath = (
            CLIPS_DIRPATH
            / media_filepath_relative
            / f"{datetime.now().strftime(r'%Y-%m-%dT%H-%M-%S.%f')} - {self.metadata['artist']}{media_file_extension}"
        )

    def create_clip(self):
        start_timestamp = timestamp_str_of(self.start_time)
        end_timestamp = timestamp_str_of(self.end_time)
        duration_timestamp = timestamp_str_of(self.end_time - self.start_time)
        logging.info(
            f"From file ({self.media_path}, {start_timestamp} - {end_timestamp} [{duration_timestamp}]), creating clip to file ({self.save_filepath})."
        )
        self.save_filepath.parent.mkdir(parents=True, exist_ok=True)
        (
            ffmpeg.input(self.media_path, ss=start_timestamp, to=end_timestamp)
            .output(
                str(self.save_filepath),
                vcodec="copy",
                acodec="copy",
                map_metadata=-1,
                **{
                    "metadata:g:0": "title={title}".format(**self.metadata),
                    "metadata:g:1": "show={show}".format(**self.metadata),
                    "metadata:g:2": "season={season}".format(**self.metadata),
                    "metadata:g:3": "episode={episode}".format(**self.metadata),
                    "metadata:g:4": "episode_timestamp={episode_timestamp}".format(**self.metadata),
                    "metadata:g:5": "artist={artist}".format(**self.metadata),
                },
            )
            .run(capture_stdout=True)
        )
        logging.info(f"Created file ({self.save_filepath}).")

    @staticmethod
    def get_all_clips() -> list[dict[str, str]]:
        return [
            Clip_.from_filepath(Path(dirpath) / filename).to_dict()
            for dirpath, _, filenames in os.walk(CLIPS_DIRPATH)
            for filename in filenames
        ]


class Clip_(object):
    def __init__(
        self,
        filepath: Path,
        title: str,
        original_start_time: str,
        username: str,
        show: str,
        season_number: int,
        episode_number: int,
    ) -> None:
        self.filepath = filepath
        self.title = title
        self.original_start_time = original_start_time
        self.username = username
        self.show = show
        self.season_number = season_number
        self.episode_number = episode_number

    def to_dict(self) -> dict[str, str]:
        return self.__dict__

    @staticmethod
    def from_filepath(filepath: Path) -> Clip_:
        metadata = ffmpeg.probe(filepath)["format"]["tags"]
        return Clip_(
            filepath=filepath.parts[1:],
            title=metadata.get("title") or "",
            original_start_time=metadata.get("comment") or "",
            username=metadata.get("artist") or "",
            show=metadata.get("show") or "",
            episode_number=metadata.get("episode_id") or "",
            season_number=metadata.get("season_number") or "",
        )
