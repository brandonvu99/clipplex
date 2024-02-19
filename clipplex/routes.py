from clipplex.forms import ClipForm
from clipplex.models.clip import Clip, RenderedClip
from clipplex.models.image import Image
from clipplex.models.plex import PlexInfo
from clipplex.models.snapshot import Snapshot
from clipplex.utils.files import delete_file
from clipplex.utils.streamable import streamable_upload
from clipplex.utils.timing import add_time
from datetime import timedelta
from flask import Flask
from flask import render_template, redirect, request, jsonify
from pprint import pformat
import logging

flaskapp = Flask(__name__, static_url_path="/static")
flaskapp.config["SECRET_KEY"] = "524t098wruigofjvncx98uwroeiyhfjdk"


@flaskapp.route("/")
def render_home():
    return redirect("/clip.html")


@flaskapp.route("/clip.html", methods=["GET"])
def render_clip():
    rendered_clips = RenderedClip.get_all_rendered_clips()
    rendered_clip_filepaths = [clip['filepath'] for clip in rendered_clips]
    logging.info(f"Serving clips from the following filepaths: {pformat(rendered_clip_filepaths)}")
    return render_template(
        "clip.html",
        form=ClipForm(),
        title="Clips",
        clips=rendered_clips,
    )


@flaskapp.route("/login.html", methods=["GET", "POST"])
def render_login():
    return render_template("login.html")


@flaskapp.route("/snapshot.html", methods=["GET"])
def render_snapshot():
    return render_template(
        "snapshot.html",
        title="Snapshot",
        images=Image.get_all_images(),
    )


@flaskapp.route("/api/clips", methods=["POST"])
def clip_create():
    args = request.args
    username = args.get("username")
    start_hour = int(args.get("start_hour"))
    start_minute = int(args.get("start_minute"))
    start_second = int(args.get("start_second"))
    end_hour = int(args.get("end_hour"))
    end_minute = int(args.get("end_minute"))
    end_second = int(args.get("end_second"))

    start = timedelta(hours=start_hour, minutes=start_minute, seconds=start_second)
    end = timedelta(hours=end_hour, minutes=end_minute, seconds=end_second)
    result = generate_clip(username, start, end)
    return jsonify(result)


def generate_clip(username: str, start_time: timedelta, end_time: timedelta):
    plex_data = PlexInfo.create_plex_info(username)
    clip = Clip(plex_data, start_time, end_time)
    clip.create_clip()
    return {"result": "success"}


@flaskapp.route("/api/clips", methods=["DELETE"])
# @login_required
def clip_delete():
    clip_path = request.args.get("filepath")
    if delete_file(clip_path):
        return redirect("/clip.html")
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
    return PlexInfo.create_plex_info(username).to_stream_info()


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
    filepath = request.args.get("filepath")
    upload = streamable_upload(filepath)
    return upload
