from app import routes
from flask import Flask
import os

flaskapp = Flask(__name__, static_url_path="/static")
flaskapp.config["SECRET_KEY"] = "524t098wruigofjvncx98uwroeiyhfjdk"