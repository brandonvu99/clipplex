from __future__ import annotations
from clipplex.config import CLIPS_DIRPATH, GENERATED_MEDIA_DIRPATH
from clipplex.models.plex import ActivePlexInfo
from clipplex.utils.timing import timestamp_str_of
from datetime import timedelta, datetime
from pathlib import Path
from pprint import pformat
import ffmpeg
import logging
import os


class Clip:
    def __init__(
        self, plex_info: ActivePlexInfo, start_time: timedelta, end_time: timedelta
    ):
        self.create_timestamp = datetime.now().strftime(r"%Y-%m-%dT%H-%M-%S.%f%z")
        self.media_path = plex_info.media_path
        self.start_timestamp = timestamp_str_of(start_time)
        self.end_timestamp = timestamp_str_of(end_time)
        self.duration_timestamp = timestamp_str_of(end_time - start_time)

        self.metadata = {
            "title": plex_info.media_title,
            "show": plex_info.show_name,
            "season": plex_info.season,
            "episode": plex_info.episode_number,
            "episode_start_timestamp": self.start_timestamp,
            "episode_end_timestamp": self.end_timestamp,
            "create_timestamp": self.create_timestamp,
            "creator": plex_info.username,
        }

        # TODO(somehow make this dynamic enough to handle output path without needing configuration from user)
        media_filepath_relative = self.media_path.relative_to(GENERATED_MEDIA_DIRPATH)
        # TODO(using the original extension available as self.media_path.suffix will make mkv files whose duration is from [start_timestamp, end_of_file] instead of [start_timestamp, end_timestamp], but the playable content is only from [start_timestamp, end_timestamp]. using mp4 for now.)
        self.save_filepath = (
            CLIPS_DIRPATH
            / media_filepath_relative
            / f"{datetime.now().strftime(r'%Y-%m-%dT%H-%M-%S.%f')} - {self.metadata['creator']}.mp4"
        )

    def create_clip(self):        
        logging.info(
            f"From file ({self.media_path}, {self.start_timestamp} - {self.end_timestamp} [{self.duration_timestamp}]), creating clip to file ({self.save_filepath})."
        )
        self.save_filepath.parent.mkdir(parents=True, exist_ok=True)
        (
            ffmpeg.input(self.media_path, ss=self.start_timestamp, to=self.end_timestamp)
            .output(
                str(self.save_filepath),
                vcodec="copy",
                # TODO(Strips all metadata?)
                map_metadata=-1,
                movflags="use_metadata_tags",
                **{
                    "metadata:g:0": "title={title}".format(**self.metadata),
                    "metadata:g:1": "show={show}".format(**self.metadata),
                    "metadata:g:2": "season={season}".format(**self.metadata),
                    "metadata:g:3": "episode={episode}".format(**self.metadata),
                    "metadata:g:4": "episode_start_timestamp={episode_start_timestamp}".format(
                        **self.metadata
                    ),
                    "metadata:g:5": "episode_end_timestamp={episode_end_timestamp}".format(
                        **self.metadata
                    ),
                    "metadata:g:6": "create_timestamp={create_timestamp}".format(
                        **self.metadata
                    ),
                    "metadata:g:7": "creator={creator}".format(**self.metadata),
                },
            )
            .run(capture_stdout=True)
        )
        logging.info(f"Created file ({self.save_filepath}).")


class RenderedClip(object):
    def __init__(
        self,
        filepath: Path,
        title: str,
        show: str,
        season: int,
        episode: int,
        episode_start_timestamp: str,
        episode_end_timestamp: str,
        create_timestamp: str,
        creator: str,
    ) -> None:
        self.filepath = filepath
        self.title = title
        self.show = show
        self.season = season
        self.episode = episode
        self.episode_start_timestamp = episode_start_timestamp
        self.episode_end_timestamp = episode_end_timestamp
        self.create_timestamp = create_timestamp
        self.creator = creator

    def to_dict(self) -> dict[str, str]:
        return self.__dict__

    @staticmethod
    def get_all_rendered_clips() -> list[dict[str, str]]:
        return [
            RenderedClip.from_filepath(Path(dirpath) / filename).to_dict()
            for dirpath, _, filenames in os.walk(CLIPS_DIRPATH)
            for filename in filenames
        ]

    @staticmethod
    def from_filepath(filepath: Path) -> RenderedClip:
        metadata = ffmpeg.probe(filepath)["format"]["tags"]
        logging.info(f"All available metadata for {filepath}: {pformat(metadata)}")
        return RenderedClip(
            filepath=RenderedClip.to_flask_static_path(filepath),
            title=metadata.get("title") or "",
            show=metadata.get("show") or "",
            season=metadata.get("season") or "",
            episode=metadata.get("episode") or "",
            episode_start_timestamp=metadata.get("episode_start_timestamp") or "",
            episode_end_timestamp=metadata.get("episode_end_timestamp") or "",
            create_timestamp=metadata.get("create_timestamp") or "",
            creator=metadata.get("creator") or "",
        )

    @staticmethod
    def to_flask_static_path(path: Path) -> Path:
        return path.relative_to("./clipplex")
