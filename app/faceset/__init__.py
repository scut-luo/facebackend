from flask import Blueprint

faceset = Blueprint('faceset', __name__)

from . import views
