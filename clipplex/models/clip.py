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
    def __init__(self, plex_data: ActivePlexInfo, start_time: timedelta, end_time: timedelta):
        self.media_path = plex_data.media_path
        plex_attributes = list(list(plex_data.media_path_xml))[0].attrib
        self.metadata_title = plex_attributes["title"]
        self.metadata_current_media_time = plex_data.current_media_time_str
        self.metadata_username = plex_data.username
        if plex_data.media_type == "episode":
            self.metadata_season = plex_attributes["parentIndex"]
            self.metadata_episode_number = plex_attributes["index"]
            self.metadata_showname = plex_attributes["grandparentTitle"]
        else:
            self.metadata_season = ""
            self.metadata_episode_number = ""
            self.metadata_showname = ""
        self.start_time = start_time
        self.end_time = end_time

        media_filepath_relative = self.media_path.relative_to("../Media")
        self.save_filepath = CLIPS_DIRPATH / media_filepath_relative / f"{datetime.now().strftime(r'%Y-%m-%dT%H-%M-%S.%f')} - {self.metadata_username}.mkv"

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
                vcodec='copy',
                acodec='copy',
                map_metadata=-1,
                **{
                    "metadata:g:0": f"title={self.metadata_title}",
                    "metadata:g:1": f"season_number={self.metadata_season}",
                    "metadata:g:2": f"show={self.metadata_showname}",
                    "metadata:g:3": f"episode_id={self.metadata_episode_number}",
                    "metadata:g:4": f"comment={self.metadata_current_media_time}",
                    "metadata:g:5": f"artist={self.metadata_username}",
                },
            )
            .run(capture_stdout=True)
        )
        logging.info(
            f"Created file ({self.save_filepath})."
        )

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
