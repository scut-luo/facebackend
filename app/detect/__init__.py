from flask import Blueprint

detect = Blueprint('detect', __name__)

from . import views
