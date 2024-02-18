from __future__ import annotations
from abc import ABC, abstractmethod
from clipplex.utils.timing import milli_to_string
from clipplex.config import (
    PLEX_TOKEN,
    PLEX_URL,
    PLEX_DIRPATH_TO_CLIPPLEX_DIRPATH,
    PLEX_REQUEST_PARAMS,
)
from pathlib import Path
import xml.etree.ElementTree as ET
import logging
import os
import requests


class PlexInfo(ABC):

    @abstractmethod
    def to_stream_info(self) -> dict[str, str]:
        pass

    @staticmethod
    def create_plex_info(username) -> PlexInfo:
        sessions_xml = PlexInfo.get_current_sessions_xml()
        logging.info(f"sessions_xml: {sessions_xml}")
        return ActivePlexInfo(username) if sessions_xml else InactivePlexInfo(username)

    @staticmethod
    def get_current_sessions_xml() -> ET.ElementTree | None:
        """Get the XML from plex for the current user session.

        Returns:
            ET.ElementTree: XML tree of the current user session
        """
        if PLEX_URL is None:
            return None

        response = requests.get(
            f"{PLEX_URL}/status/sessions", params=PLEX_REQUEST_PARAMS
        )
        xml_content = ET.ElementTree(ET.fromstring(response.content))
        return xml_content


class InactivePlexInfo(PlexInfo):
    def __init__(self, username) -> None:
        self.username = username

    def to_stream_info(self) -> dict[str, str]:
        return {"message": f"No session running for user {self.username}."}


class ActivePlexInfo(PlexInfo):
    def __init__(self, username):
        self.plex_token = PLEX_TOKEN
        self.plex_url = PLEX_URL
        self.params = (("X-Plex-Token", {self.plex_token}),)
        self.sessions_xml = PlexInfo.get_current_sessions_xml()
        with open("sessions.xml", "w") as f:
            self.sessions_xml.write(f, encoding="unicode")
        self.username = username
        self.session_id = self._get_session_id(username)
        self.media_key = self._get_media_key()
        self.media_path_xml = self._get_media_path_xml()
        self.media_path: Path = self._get_file_path()
        self.media_fps = self._get_media_fps()
        self.media_type = self._get_file_type()
        self.media_title = self._get_file_title()
        self.current_media_time_int = self._get_current_media_time()
        self.current_media_time_str = milli_to_string(self.current_media_time_int)

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

    def _get_media_fps(self) -> float:
        """Get the frame rate of the video currently played by the user.

        Returns:
            float: Frame Rate of the video
        """

        media_element = self.sessions_xml.findall("./MediaContainer/Video/Media/Part/Stream[@streamType=1]")
        

        media_dict = list(list(list(list(list(self.media_path_xml)[0]))[0])[0])[
            0
        ].attrib
        return float(media_dict["frameRate"])

    def _get_current_media_time(self) -> int:
        """Get the offset between the start of the video and the current view position of the user.

        Returns:
            int: Offset between start of the video and current view time
        """
        media_dict = list(list(self.sessions_xml))[self.session_id].attrib
        return int(media_dict["viewOffset"])

    def _get_file_path(self) -> Path:
        """Get the file path of the video currently played by the user.

        Returns:
            str: Path of the video being played
        """
        media_dict = list(list(list(list(self.media_path_xml)[0]))[0])[
            0
        ].attrib  # REPLACE THAT BY A FIND PART TAG
        plex_filepath = Path(media_dict["file"])
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
            video_dict = list(list(self.media_path_xml))[0].attrib
            title = video_dict["title"]
            show_name = video_dict["grandparentTitle"]
            return f"{show_name} - {title}"
        else:
            video_dict = list(list(self.media_path_xml))[0].attrib
            return video_dict["title"]

    def _get_file_type(self) -> str:
        """Get the type of file of the video currently played by the user.

        Returns:
            str: File type of the video being played
        """
        video_dict = list(list(self.media_path_xml))[0].attrib
        return video_dict["type"]

    def _get_media_path_xml(self) -> ET.ElementTree:
        """Get the XML from plex for the current user session.

        Returns:
            Element: XML tree of the current video being played
        """
        response = requests.get(f"{self.plex_url}{self.media_key}", params=self.params)
        xml_content = ET.ElementTree(ET.fromstring(response.content))
        return xml_content

    def _get_media_key(self) -> str:
        """Get the plex media key of the video being played.

        Returns:
            str: Plex media key
        """
        media_info = list(list(self.sessions_xml))[self.session_id].attrib
        return media_info["key"]

    def _get_session_id(self, username: str) -> int:
        """Get the plex session id of the current session for the current user.

        Args:
            username (str): Username of the queried user.

        Returns:
            int: Return the index of the session
        """
        for sessions in list(self.sessions_xml):
            for session in sessions:
                if session.tag == "User" and session.attrib["title"] == username:
                    return list(self.sessions_xml).index(sessions)
        raise Exception(f"No stream running for user {username}")

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
