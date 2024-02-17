from utils.timing import milli_to_string
import os
import xml.etree.ElementTree as ET
import requests


class PlexInfo:
    def __init__(self, username):
        self.plex_url = os.environ.get("PLEX_URL")
        self.plex_token = os.environ.get("PLEX_TOKEN")
        self.params = (("X-Plex-Token", {self.plex_token}),)
        self.sessions_xml = self._get_current_sessions_xml()
        self.username = username
        self.session_id = self._get_session_id(username)
        self.media_key = self._get_media_key()
        self.media_path_xml = self._get_media_path_xml()
        self.media_path = self._get_file_path()
        self.media_fps = self._get_media_fps()
        self.media_type = self._get_file_type()
        self.media_title = self._get_file_title()
        self.current_media_time_int = self._get_current_media_time()
        self.current_media_time_str = milli_to_string(self.current_media_time_int)

    def _get_media_fps(self) -> float:
        """Get the frame rate of the video currently played by the user.

        Returns:
            float: Frame Rate of the video
        """
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

    def _get_current_sessions_xml(self) -> ET:
        """Get the XML from plex for the current user session.

        Returns:
            ET: XML tree of the current user session
        """
        response = requests.get(f"{self.plex_url}/status/sessions", params=self.params)
        xml_content = ET.fromstring(response.content)
        return xml_content

    def _get_file_path(self) -> str:
        """Get the file path of the video currently played by the user.

        Returns:
            str: Path of the video being played
        """
        media_dict = list(list(list(list(self.media_path_xml)[0]))[0])[
            0
        ].attrib  # REPLACE THAT BY A FIND PART TAG
        return media_dict["file"]

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

    def _get_media_path_xml(self) -> ET:
        """Get the XML from plex for the current user session.

        Returns:
            ET: XML tree of the current video being played
        """
        response = requests.get(f"{self.plex_url}{self.media_key}", params=self.params)
        xml_content = ET.fromstring(response.content)
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
