from flask import abort, request
from flask_smorest import Blueprint
from flask.views import MethodView


blp = Blueprint("course_items", __name__, description="Operations on course_items")

@blp.route('/')
def home():
    return "<h1>Book Fair zebi</h1>"