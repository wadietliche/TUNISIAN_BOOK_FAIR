from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema,BookSearchSchema, AuthorSearchSchema
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask import jsonify
from webapp.Services import AttendeeServices



attendee_bp = Blueprint("Attendees", "attendees", description="Operations on Attendees")



# Attendee Sign-up (POST request to create a new attendee)
@attendee_bp.route("/attendee/signup")
class AttendeeSignup(MethodView):
    @attendee_bp.arguments(AttendeeSchema)
    @attendee_bp.response(201, AttendeeSchema)
    def post(self, attendee_data):
        return AttendeeServices.attendeeSignUp(attendee_data)



# Attendee Login (POST request to authenticate)
@attendee_bp.route("/attendee/login")
class AttendeeLogin(MethodView):
    @attendee_bp.arguments(AttendeeLoginSchema)
    def post(self,login_data):
        return AttendeeServices.attendeeLogin(login_data)



# Add to Favorite Books (POST request to mark a book as favorite)
@attendee_bp.route("/attendee/favorite/book")
class AddFavoriteBook(MethodView):
    @attendee_bp.arguments(FavoriteBookSchema)
    def post(self, favorite_book_data):
        return AttendeeServices.addFavoriteBook(favorite_book_data)



# Add to Favorite Authors (POST request to mark an author as favorite)
attendee_bp.route("/attendee/favorite/author", methods=["POST"])
class AddFavoriteAuthor(MethodView):
    @attendee_bp.arguments(FavoriteAuthorSchema)
    def post(self, favorite_author_data):
       return AttendeeServices.addFavoriteAuthor(favorite_author_data)



# Check if Author is Attending (GET request to check if an author is attending an event)
@attendee_bp.route("/attendee/author/<int:author_id>/attending")
class CheckAuthorAttendance(MethodView):
    def get(self, author_id):
       return AttendeeServices.checkAuthorAttendence(author_id)



# Attend an Event (POST request to mark attendance)
@attendee_bp.route("/attendee/event/attend")
class AttendEvent(MethodView):
    @attendee_bp.arguments(EventAttendanceSchema)
    def post(self, attendance_data):
        return AttendeeServices.confirmAttendance(attendance_data)


# Book Search Route
@attendee_bp.route("/attendee/search/book", methods=["GET"])
class BookSearch(MethodView):
    @attendee_bp.arguments(BookSearchSchema, location="query")
    def get(self, search_data):
        return AttendeeServices.bookSearch(search_data)


# Author Search Route
@attendee_bp.route("/attendee/search/author", methods=["GET"])
class AuthorSearch(MethodView):
    @attendee_bp.arguments(AuthorSearchSchema, location="query")
    def get(self, search_data):
        return AttendeeServices.authorSearch(search_data)