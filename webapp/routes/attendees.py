from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author, FairMap
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, ChatbotSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema,CombinedSearchSchema,RecommendationResponseSchema,RecommendationRequestSchema
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask import jsonify,Response,request
from webapp.Services import AttendeeServices, RecommendationServices, ChatbotServices
from flask_jwt_extended import jwt_required, get_jwt,get_jwt_identity


attendee_bp = Blueprint("Attendees", "attendees", description="Operations on Attendees")



# Attendee Sign-up 
@attendee_bp.route("/attendee/signup")
class AttendeeSignup(MethodView):
    @attendee_bp.arguments(AttendeeSchema)
    @attendee_bp.response(201, AttendeeSchema)
    def post(self, attendee_data):
        return AttendeeServices.attendeeSignUp(attendee_data)



# Attendee Login 
@attendee_bp.route("/attendee/login")
class AttendeeLogin(MethodView):
    @attendee_bp.arguments(AttendeeLoginSchema)
    def post(self,login_data):
        return AttendeeServices.attendeeLogin(login_data)


#done
# Add to Favorite Books 
@attendee_bp.route("/attendee/favorite/book")
class AddFavoriteBook(MethodView):
    
    @jwt_required() 
    @attendee_bp.arguments(FavoriteBookSchema)
    def post(self, favorite_book_data):
        try:
            claims = get_jwt()
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: Attendee privileges are required to access this endpoint."
                }), 403

            return AttendeeServices.add_favorite_book(favorite_book_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500



@attendee_bp.route("/attendee/favorite/author", methods=["POST"])
class AddFavoriteAuthor(MethodView):
    @jwt_required() 
    @attendee_bp.arguments(FavoriteAuthorSchema)
    def post(self,favorite_author_data):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            return AttendeeServices.add_favorite_author(favorite_author_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500



@attendee_bp.route("/attendee/event/attend", methods=["POST"])
class AttendEvent(MethodView):
    @jwt_required() 
    @attendee_bp.arguments(EventAttendanceSchema)
    def post(self, attendance_data):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            return AttendeeServices.confirmAttendance(attendance_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


@attendee_bp.route("/attendee/search")
class SearchBook(MethodView):
    @jwt_required()
    @attendee_bp.arguments(CombinedSearchSchema, location="query")
    def get(self, search_data):
            try:
                claims = get_jwt()  # Get the JWT claims
                if not (claims.get("is_admin") or claims.get("is_attendee")):
                    return jsonify({
                        "message": "Access denied: You must be an attendee to access this resource."
                    }), 403
                result = AttendeeServices.combinedSearch(search_data)

                if isinstance(result, Response):
                    return result  
                return jsonify(result)  

            except Exception as e:
                return jsonify({"error": str(e)}), 500
    


#Book recommendation 
@attendee_bp.route("/attendee/recommend")
class RecommendBooks(MethodView):
    decorators = [jwt_required()]  

    @attendee_bp.arguments(RecommendationRequestSchema)
    @attendee_bp.response(200, RecommendationResponseSchema)
    def post(self, attendee_data):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            return RecommendationServices.recommend_books_for_attendee(attendee_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    


@attendee_bp.route("/attendee/event/<int:event_id>", methods=["GET", "POST", "PUT"])
class EventInfo(MethodView):
    @jwt_required()  
    def get(self, event_id):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            return AttendeeServices.getEventInfo(event_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  
    def post(self, event_id):
        try:
            claims = get_jwt() 
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403

            return AttendeeServices.ConfirmAttendence(event_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  
    def put(self, event_id):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            return AttendeeServices.giveFeedback(event_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500



@attendee_bp.route("/attendee/approved-authors-booths", methods=["GET", "POST"])
class ApprovedAuthorsBooths(MethodView):
    @jwt_required()  
    def get(self):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            return AttendeeServices.getAuthorBooths()

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  
    def post(self):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an attendee to access this resource."
                }), 403


            return AttendeeServices.getAuthorBoothByName()

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    

@attendee_bp.route("/attendee/chatbot", methods=["POST"])
class Chatbot(MethodView):
    @jwt_required()
    @attendee_bp.arguments(ChatbotSchema)  # Validate input using a schema
    def post(self, chatbot_data):
        try:
            # Check user permissions
            claims = get_jwt()
            if not (claims.get("is_admin") or claims.get("is_attendee")):
                return jsonify({
                    "message": "Access denied: You must be an attendee to access this resource."
                }), 403

            # Extract the user's message and context
            user_input = chatbot_data.get("message")
            context = chatbot_data.get("context", "")
            attendee_id = int(get_jwt_identity())

            if not user_input:
                return jsonify({"error": "No message provided"}), 400

            # Call the service layer to generate a response
            response = ChatbotServices.generate_chatbot_response(user_input, context, attendee_id)
            return jsonify({"response": response})

        except Exception as e:
            return jsonify({"error": str(e)}), 500