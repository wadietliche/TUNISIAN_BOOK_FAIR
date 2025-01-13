from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema,CombinedSearchSchema,RecommendationResponseSchema,RecommendationRequestSchema
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask import jsonify,Response
from webapp.Services import AttendeeServices, RecommendationServices
from flask_jwt_extended import jwt_required


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
        return AttendeeServices.add_favorite_book(favorite_book_data)



@attendee_bp.route("/attendee/favorite/author", methods=["POST"])
class AddFavoriteAuthor(MethodView):
    @attendee_bp.arguments(FavoriteAuthorSchema)
    def post(self, favorite_author_data):
        return AttendeeServices.add_favorite_author(favorite_author_data)




# Check if Author is Attending (GET request to check if an author is attending an event)
@attendee_bp.route("/attendee/author/<int:author_id>/attending")
@jwt_required()
class CheckAuthorAttendance(MethodView):
    def get(self, author_id):
       return AttendeeServices.checkAuthorAttendence(author_id)



# Attend an Event (POST request to mark attendance)
@attendee_bp.route("/attendee/event/attend")
@jwt_required()
class AttendEvent(MethodView):
    @attendee_bp.arguments(EventAttendanceSchema)
    def post(self, attendance_data):
        return AttendeeServices.confirmAttendance(attendance_data)


# Book Search Route
@attendee_bp.route("/attendee/search")
class CombinedSearch(MethodView):
    """
    Allows searching for books by both title and author name.
    """
    decorators = [jwt_required()]  # Apply decorators to the class

    @attendee_bp.arguments(CombinedSearchSchema, location="query")
    def get(self, search_data):
        # Use the service to process the search request
        result = AttendeeServices.combinedSearch(search_data)

        # Check if the result is a Response object (error or valid response)
        if isinstance(result, Response):
            return result  # Return the existing Response object

        # If the result is not a Response, jsonify it before returning
        return jsonify(result)  # Ensure response is in Flask's JSON format
    


#Book recommendation 
@attendee_bp.route("/attendee/recommend")
class RecommendBooks(MethodView):
    @attendee_bp.arguments(RecommendationRequestSchema)
    @attendee_bp.response(200, RecommendationResponseSchema)
    def post(self, attendee_data):
       return RecommendationServices.recommend_books_for_attendee(attendee_data)
    