from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import timedelta
from clipplex.utils.timing import timestamp_str_of
from clipplex.config import (
    PLEX_TOKEN,
    PLEX_URL,
    PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH
)
from pathlib import Path
import xml.etree.ElementTree as ET
import logging
import os
from plexapi.server import PlexServer
from plexapi.media import Media
from plexapi.video import Show, Movie


plex = PlexServer(PLEX_URL, PLEX_TOKEN)


class PlexInfo(ABC):
    """
    Treat PlexInfo and all of its subclasses as immutable, i.e. values are not updated as time passes.
    Create a new PlexInfo object if up-to-date information is needed.
    """

    @abstractmethod
    def to_stream_info(self) -> dict[str, str]:
        pass

    @staticmethod
    def create_plex_info(username) -> PlexInfo:
        sessions = PlexInfo.get_current_sessions()
        return (
            ActivePlexInfo(username, sessions)
            if sessions
            else InactivePlexInfo(username)
        )

    @staticmethod
    def get_current_sessions() -> list[Media] | None:
        sessions: list[Media] = plex.sessions()
        return sessions if sessions else None


class InactivePlexInfo(PlexInfo):
    def __init__(self, username) -> None:
        self.username = username

    def to_stream_info(self) -> dict[str, str]:
        return {"message": f"No session running for user {self.username}."}


class ActivePlexInfo(PlexInfo):
    def __init__(self, username: str, sessions: list[Media]):
        self.username = username
        self.session = sessions[0]
        self.media_path: Path = self._get_translated_filepath()
        self.media_type = self.session.type
        self.media_title = self._get_file_title()
        self.current_media_time_str = timestamp_str_of(
            timedelta(self.session.viewOffset)
        )

    def __bool__(self) -> bool:
        return self.sessions_xml is not None

    def to_stream_info(self) -> dict[str, str]:
        return (
            {
                "file_path": str(self.media_path),
                "username": self.username,
                "current_time": self.current_media_time_str,
                "media_title": self.media_title,
            }
            if self.sessions_xml is not None
            else {"message": f"No session running for user {self.username}."}
        )

    def _get_filepath(self) -> Path:
        """Get the file path of the video currently played by the user.

        Returns:
            str: Path of the video being played
        """

        for media in plex.library.sectionByID(self.session.librarySectionID).all():
            if self.media_type == "episode":
                if self.session.grandparentGuid == show.guid:
                    show: Show = media
                    season = show.season(title=self.session.parentTitle)
                    episode = season.episode(title=self.session.title)

                    return Path(episode.locations[0])
            elif self.media_type == "movie":
                if self.session.guid == media.guid:
                    movie: Movie = media

                    return Path(movie.locations[0])

        raise ValueError(
            f"Following session could not be mapped to a media file: {self.session}"
        )

    def _get_translated_filepath(self) -> Path:
        plex_filepath = self._get_filepath()
        clipplex_filepath = ActivePlexInfo.plex_filepath_to_clipplex_filepath(
            plex_filepath
        )
        return clipplex_filepath

    def _get_file_title(self) -> str:
        """Get the title of the video currently played by the user.

        Returns:
            str: If TV show, returns show + episode name, if movie, returns movie name.
        """
        if self.media_type == "episode":
            show_name = self.session.grandparentTitle
            title = self.session.title
            return f"{show_name} - {title}"
        elif self.media_type == "movie":
            return self.session.title

        raise ValueError(f"Unsupported media_type: {self.media_type}")

    @staticmethod
    def plex_filepath_to_clipplex_filepath(plex_filepath: Path) -> Path:
        """
        Converts a given plex filepath to its respective clipplex filepath based off of the mapping {PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH}.
        The most specific (or lowest common ancestor) of all {PLEX_DIRPATH}s for the given plex filepath is chosen. For example, for the following mapping:

        PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH = {
            "/long/plex/path/to/media/" : "/clipplex/Media/",
            "/long/plex/path/to/media/but/more/specific/" : "/clipplex/other/media/dir/",
        }

        a plex filepath of "/long/plex/path/to/media/but/more/specific/Drag Race/s01e01.mkv" will be mapped to "/clipplex/other/media/dir/Drag Race/s01e01.mkv"
        because even though "/long/plex/path/to/media/" COULD match, the more specific one matches.
        """

        plex_dirpath_ancestors = [
            plex_dirpath
            for plex_dirpath in PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH.keys()
            if plex_filepath.is_relative_to(plex_dirpath)
        ]
        if not plex_dirpath_ancestors:
            raise ValueError(
                f"The given plex_filepath ({plex_filepath}) does not have an associated mapping in PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH."
            )
        most_specific_plex_dir = Path(os.path.commonpath(plex_dirpath_ancestors))

        clipplex_dirpath = PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH[most_specific_plex_dir]
        relative_filepath = plex_filepath.relative_to(most_specific_plex_dir)

        clipplex_clip_filepath = clipplex_dirpath / relative_filepath
        logging.info(f"Translated ({plex_filepath}) to ({clipplex_clip_filepath})")
        return clipplex_clip_filepath
