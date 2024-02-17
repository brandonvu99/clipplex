from app import routes
from flask import Flask
import os

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "524t098wruigofjvncx98uwroeiyhfjdk"