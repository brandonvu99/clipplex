from clipplex.models.plex import PlexInfo
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Optional, Length
from wtforms.widgets import Input


class ButtonField(BooleanField):
    widget = Input(input_type="button")


class ClipForm(FlaskForm):
    # user = StringField("Username", [DataRequired()])
    username = SelectField(label="Username", choices=PlexInfo.get_all_connected_usernames())
    start_time_hour = StringField([Length(min=2, max=2)])
    start_time_minute = StringField([Length(min=2, max=2)])
    start_time_sec = StringField([Length(min=2, max=2)])
    end_time_hour = StringField([Length(min=2, max=2)])
    end_time_minute = StringField([Length(min=2, max=2)])
    end_time_sec = StringField([Length(min=2, max=2)])
    check_stream_info_btn = ButtonField()
    submit = SubmitField("Create clip")
