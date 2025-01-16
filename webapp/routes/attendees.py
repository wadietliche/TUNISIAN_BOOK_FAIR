from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author, FairMap
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema,CombinedSearchSchema,RecommendationResponseSchema,RecommendationRequestSchema
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask import jsonify,Response
from webapp.Services import AttendeeServices, RecommendationServices
from flask_jwt_extended import jwt_required, get_jwt


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


#done
# Add to Favorite Books (POST request to mark a book as favorite)
@attendee_bp.route("/attendee/favorite/book")
class AddFavoriteBook(MethodView):
    
    @jwt_required()  # Ensure the user is authenticated
    @attendee_bp.arguments(FavoriteBookSchema)
    def post(self, favorite_book_data):
        try:
            # Retrieve JWT claims
            claims = get_jwt()
            
            # Check if the claim has is_admin or is_attendee
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: Administrator or Attendee privileges are required to access this endpoint."
                }), 403

            # If the user has valid claims, proceed with adding the favorite book
            return AttendeeServices.add_favorite_book(favorite_book_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500



@attendee_bp.route("/attendee/favorite/author", methods=["POST"])
class AddFavoriteAuthor(MethodView):
    @jwt_required()  # Ensure that JWT is required for this endpoint
    def post(self, favorite_author_data):
        """
        Endpoint to add a favorite author for the attendee.
        Only accessible if the user has is_admin=True or is_attendee=True in the JWT claims.
        """
        try:
            claims = get_jwt()  # Get the JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # If the claim is valid, proceed to add favorite author
            return AttendeeServices.add_favorite_author(favorite_author_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500




# Attend an Event (POST request to mark attendance)
@attendee_bp.route("/attendee/event/attend", methods=["POST"])
class AttendEvent(MethodView):
    @jwt_required()  # Ensure that JWT is required for this endpoint
    @attendee_bp.arguments(EventAttendanceSchema)
    def post(self, attendance_data):
        """
        Endpoint to confirm attendance at an event.
        Only accessible if the user has is_admin=True or is_attendee=True in the JWT claims.
        """
        try:
            claims = get_jwt()  # Get the JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # If the claim is valid, proceed to confirm attendance
            return AttendeeServices.confirmAttendance(attendance_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Book Search Route
@attendee_bp.arguments(CombinedSearchSchema, location="query")
def get(self, search_data):
        """
        Endpoint to search books by title and author. 
        Only accessible if the user has is_admin=True or is_attendee=True in the JWT claims.
        """
        try:
            claims = get_jwt()  # Get the JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Use the service to process the search request
            result = AttendeeServices.combinedSearch(search_data)

            # Check if the result is a Response object (error or valid response)
            if isinstance(result, Response):
                return result  # Return the existing Response object

            # If the result is not a Response, jsonify it before returning
            return jsonify(result)  # Ensure response is in Flask's JSON format

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    


#Book recommendation 
@attendee_bp.route("/attendee/recommend")
class RecommendBooks(MethodView):
    """
    Endpoint to recommend books for an attendee. 
    Only accessible if the user has is_admin=True or is_attendee=True in the JWT claims.
    """
    decorators = [jwt_required()]  # Apply decorators to the class

    @attendee_bp.arguments(RecommendationRequestSchema)
    @attendee_bp.response(200, RecommendationResponseSchema)
    def post(self, attendee_data):
        """
        Endpoint to recommend books for an attendee. 
        Only accessible if the user is either an admin or an attendee.
        """
        try:
            claims = get_jwt()  # Get the JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Proceed with the recommendation process
            return RecommendationServices.recommend_books_for_attendee(attendee_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    


@attendee_bp.route("/attendee/event/<int:event_id>", methods=["GET", "POST", "PUT"])
class EventInfo(MethodView):
    """
    Endpoint for event-related actions (Get event info, Post attendance confirmation, and Put feedback).
    Only accessible if the user has is_admin=True or is_attendee=True in the JWT claims.
    """

    @jwt_required()  # Ensure the user is authenticated
    def get(self, event_id):
        """
        Retrieve event information.
        """
        try:
            claims = get_jwt()  # Get JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Proceed with retrieving event info
            return AttendeeServices.getEventInfo(event_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  # Ensure the user is authenticated
    def post(self, event_id):
        """
        Confirm attendance for an event.
        """
        try:
            claims = get_jwt()  # Get JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Confirm attendance
            return AttendeeServices.ConfirmAttendence(event_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  # Ensure the user is authenticated
    def put(self, event_id):
        """
        Submit feedback for an event.
        """
        try:
            claims = get_jwt()  # Get JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Submit feedback for the event
            return AttendeeServices.giveFeedback(event_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500



@attendee_bp.route("/attendee/approved-authors-booths", methods=["GET", "POST"])
class ApprovedAuthorsBooths(MethodView):
    """
    Endpoint for getting approved authors' booths information.
    Only accessible if the user has is_admin=True or is_attendee=True in the JWT claims.
    """

    @jwt_required()  # Ensure the user is authenticated
    def get(self):
        """
        Retrieve approved authors' booths.
        """
        try:
            claims = get_jwt()  # Get JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Retrieve the list of approved authors' booths
            return AttendeeServices.getAuthorBooths()

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  # Ensure the user is authenticated
    def post(self):
        """
        Retrieve author booth by name.
        """
        try:
            claims = get_jwt()  # Get JWT claims
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            # Retrieve the author booth by name
            return AttendeeServices.getAuthorBoothByName()

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    