from clipplex.forms import videoForm
from clipplex.models.plex import PlexInfo
from clipplex.models.snapshot import Snapshot
from clipplex.models.video import Video
from clipplex.utils import timing
from clipplex.utils.files import delete_file, get_images, get_instant_videos
from clipplex.utils.streamable import streamable_upload
from clipplex.utils.timing import add_time, create_timestamp_str
from flask import Flask
from flask import render_template, redirect, request, jsonify
import time

flaskapp = Flask(__name__, static_url_path="/static")
flaskapp.config["SECRET_KEY"] = "524t098wruigofjvncx98uwroeiyhfjdk"


@flaskapp.route("/")
def home():
    return redirect("/instant_video.html")


@flaskapp.route("/create_video", methods=["POST"])
def create_video():
    args = request.args
    username = args.get("username")
    start_hour = args.get('start_hour')
    start_minute = args.get('start_minute')
    start_second = args.get('start_second')
    end_hour = args.get('end_hour')
    end_minute = args.get('end_minute')
    end_second = args.get('end_second')

    start_timestamp = create_timestamp_str(start_hour, start_minute, start_second)
    end_timestamp = create_timestamp_str(end_hour, end_minute, end_second)
    result = get_instant_video(username, start_timestamp, end_timestamp)
    return jsonify(result)


def get_instant_video(username, start, end):
    plex_data = PlexInfo(username)
    clip_time = timing.calculate_clip_time(start, end)
    media_name = plex_data.media_title.replace(" ", "")
    file_name = f"{username}_{media_name}_{int(time.time())}"
    current_media_time = plex_data.current_media_time_str
    # TODO(use logging library instead of print)
    print(
        f"Creating video of {clip_time} seconds starting at {start} for user {username} for file {plex_data.media_path}"
    )
    video = Video(plex_data, start, clip_time, file_name)
    video.extract_video()
    return {"result": "success"}


@flaskapp.route("/get_current_stream", methods=["GET", "POST"])
def get_current_stream():
    username = request.args.get("username")
    try:
        plex = PlexInfo(username)
    except:
        return {"message": f"No session running for user {username}"}
    return {
        "file_path": str(plex.media_path),
        "username": username,
        "current_time": plex.current_media_time_str,
        "media_title": plex.media_title,
    }


@flaskapp.route("/get_instant_snapshot", methods=["GET"])
def get_instant_snapshot():
    plex_data = PlexInfo("jonike")  # DEBUG
    snapshot = Snapshot(
        plex_data.media_path, plex_data.current_media_time_str, plex_data.media_fps
    )
    snapshot._download_frames()
    return "Files downloaded"


@flaskapp.route("/instant_snapshot.html", methods=["GET"])
def instant_snapshot():
    return render_template(
        "instant_snapshot.html",
        title="Instant Snapshot",
        images=get_images(),
    )


@flaskapp.route("/instant_video.html", methods=["GET"])
def instant_video():
    return render_template(
        "instant_video.html",
        form=videoForm(),
        title="Instant Video",
        videos=get_instant_videos(),
    )


@flaskapp.route("/login.html", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@flaskapp.route("/quick_add_time_to_start_time", methods=["POST"])
def quick_add_time_to_start_time():
    start_time = request.args.get("start_time")
    time_to_add = int(request.args.get("time_to_add"))
    return add_time(start_time, time_to_add)


@flaskapp.route("/remove_file", methods=["POST"])
# @login_required
def remove_file():
    video_path = request.args.get("file_path")
    if delete_file(video_path):
        return redirect("/instant_video.html")
    else:
        return "Problem downloading the file"


@flaskapp.route("/signin", methods=["POST"])
def signin():
    token = request.get_json()["token"]
    valid_login, user_details, user_group = check_credentials(token=token)
    print(valid_login, user_details, user_group)


def check_credentials(token=None):
    """Verifies credentials for username and password.
    Returns True and the user group on success or False and no user group"""
    plex_login = plex_user_login(token=token)

    if plex_login is not None:
        return True, plex_login[0], plex_login[1]


def plex_user_login():
    raise NotImplemented("TODO(please implement this)")


@flaskapp.route("/streamable_upload", methods=["POST"])
def streamable_upload():
    file_path = request.args.get("file_path")
    upload = streamable_upload(file_path)
    return upload
