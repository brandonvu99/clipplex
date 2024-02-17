from __future__ import annotations
from clipplex.config import MEDIA_DIR_PATH
from clipplex.models.plex import PlexInfo
from pathlib import Path
import ffmpeg


class Video:
    def __init__(self, plex_data: PlexInfo, time: str, duration, file_name: str):
        self.media_path = plex_data.media_path
        plex_attributes = list(list(plex_data.media_path_xml))[0].attrib
        self.metadata_title = plex_attributes["title"]
        self.metadata_current_media_time = plex_data.current_media_time_str
        print(plex_data.username)
        self.metadata_username = plex_data.username
        if plex_data.media_type == "episode":
            self.metadata_season = plex_attributes["parentIndex"]
            self.metadata_episode_number = plex_attributes["index"]
            self.metadata_showname = plex_attributes["grandparentTitle"]
        else:
            self.metadata_season = ""
            self.metadata_episode_number = ""
            self.metadata_showname = ""
        self.time = time
        self.duration = duration
        self.file_name = file_name

    def extract_video(self):
        (
            ffmpeg.input(self.media_path, ss=self.time, t=self.duration)
            .output(
                f"{MEDIA_DIR_PATH}/videos/{self.file_name}.mp4",
                map_metadata=-1,
                vcodec="libx264",
                acodec="libvorbis",
                pix_fmt="yuv420p",
                crf=18,
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


class Video_(object):
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
    def from_filepath(filepath: Path) -> Video_:
        metadata = ffmpeg.probe(filepath)["format"]["tags"]
        return Video_(
            filepath=filepath.parts[1:],
            title=metadata.get("title") or "",
            original_start_time=metadata.get("comment") or "",
            username=metadata.get("artist") or "",
            show=metadata.get("show") or "",
            episode_number=metadata.get("episode_id") or "",
            season_number=metadata.get("season_number") or "",
        )
