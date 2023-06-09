from flask import Blueprint

db = Blueprint('errors', __name__)

from app.errors import handlers