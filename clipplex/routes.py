from clipplex.forms import VideoForm
from clipplex.models.plex import PlexInfo
from clipplex.models.snapshot import Snapshot
from clipplex.models.video import Video
from clipplex.utils import timing
from clipplex.utils.files import delete_file, get_images, get_videos
from clipplex.utils.streamable import streamable_upload
from clipplex.utils.timing import add_time, timestamp_str_of
from datetime import timedelta
from flask import Flask
from flask import render_template, redirect, request, jsonify
from pathlib import Path
import logging
import time

flaskapp = Flask(__name__, static_url_path="/static")
flaskapp.config["SECRET_KEY"] = "524t098wruigofjvncx98uwroeiyhfjdk"


@flaskapp.route("/")
def render_home():
    return redirect("/video.html")


@flaskapp.route("/video.html", methods=["GET"])
def render_video():
    return render_template(
        "video.html",
        form=VideoForm(),
        title="Videos",
        videos=get_videos(),
    )


@flaskapp.route("/login.html", methods=["GET", "POST"])
def render_login():
    return render_template("login.html")


@flaskapp.route("/snapshot.html", methods=["GET"])
def render_snapshot():
    return render_template(
        "snapshot.html",
        title="Snapshot",
        images=get_images(),
    )


@flaskapp.route("/api/videos", methods=["POST"])
def video_create():
    args = request.args
    username = args.get("username")
    start_hour = args.get("start_hour")
    start_minute = args.get("start_minute")
    start_second = args.get("start_second")
    end_hour = args.get("end_hour")
    end_minute = args.get("end_minute")
    end_second = args.get("end_second")

    start = timedelta(hours=start_hour, minutes=start_minute, seconds=start_second)
    end = timedelta(hours=end_hour, minutes=end_minute, seconds=end_second)
    result = get_video(username, start, end)
    return jsonify(result)


def get_video(username: str, start: timedelta, end: timedelta):
    plex_data = PlexInfo(username)
    clip_duration_secs = (start - end).total_seconds()
    media_name = plex_data.media_title.replace(" ", "-")
    video_filepath = Path(username) / media_name / f"{int(time.time())}"
    logging.info(
        f"Creating video of {clip_duration_secs} seconds starting at {start} for user {username} for file {plex_data.media_path}."
    )
    video = Video(plex_data, start, clip_duration_secs, video_filepath)
    video.extract_video()
    logging.info(
        f"Created video of {clip_duration_secs} seconds starting at {start} for user {username} for file {plex_data.media_path}."
    )
    return {"result": "success"}


@flaskapp.route("/api/videos", methods=["DELETE"])
# @login_required
def video_delete():
    video_path = request.args.get("file_path")
    if delete_file(video_path):
        return redirect("/video.html")
    else:
        return "Problem deleting the file"


@flaskapp.route("/api/snapshots", methods=["GET"])
def snapshot_create():
    plex_data = PlexInfo("jonike")  # DEBUG
    snapshot = Snapshot(
        plex_data.media_path, plex_data.current_media_time_str, plex_data.media_fps
    )
    snapshot._download_frames()
    return "Files downloaded"


@flaskapp.route("/api/streams", methods=["GET"])
@flaskapp.route("/api/streams/<username>")
def stream_get(username):
    return PlexInfo(username).to_stream_info()


# TODO(make this a client side function or create a util api)
@flaskapp.route("/quick_add_time_to_start_time", methods=["POST"])
def quick_add_time_to_start_time():
    start_time = request.args.get("start_time")
    time_to_add = int(request.args.get("time_to_add"))
    return add_time(start_time, time_to_add)


@flaskapp.route("/api/signin", methods=["POST"])
def signin():
    token = request.get_json()["token"]
    valid_login, user_details, user_group = check_credentials(token=token)
    logging.info(valid_login, user_details, user_group)


def check_credentials(token=None):
    """Verifies credentials for username and password.
    Returns True and the user group on success or False and no user group"""
    plex_login = plex_user_login(token=token)

    if plex_login is not None:
        return True, plex_login[0], plex_login[1]


def plex_user_login():
    raise NotImplemented("TODO(please implement this)")


@flaskapp.route("/api/streamable", methods=["POST"])
def streamable_upload():
    file_path = request.args.get("file_path")
    upload = streamable_upload(file_path)
    return upload
