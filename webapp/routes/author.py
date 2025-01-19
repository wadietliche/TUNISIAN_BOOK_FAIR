from flask import Blueprint, request, jsonify
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from webapp import db
from webapp.models import Author, Book, FairMap, PresentEvent, Event
from webapp.schemas import AuthorSchema, BookSchema, ReservationRequestSchema,AuthorLoginSchema
from sqlalchemy.exc import SQLAlchemyError
from webapp.Services import AuthorSercices
from flask_jwt_extended import jwt_required,get_jwt



author_bp = Blueprint("authors", __name__, description="Operations related to Authors")



@author_bp.route("/author/signup", methods=["POST"])
class AuthorSignup(MethodView):
    def post(self):
        return AuthorSercices.authorSignUp()



# Route for author login
@author_bp.route("/author/login", methods=["POST"])
class AuthorLogin(MethodView):
    @author_bp.arguments(AuthorLoginSchema)
    def post(self,login_data):
        return AuthorSercices.authorLogin(login_data)



# Route to add a new book
class AddBook(MethodView):
    @author_bp.arguments(BookSchema)
    @jwt_required()  
    def post(self, book_data):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_author")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an author to access this resource."
                }), 403

            return AuthorSercices.addBookByAuthor(book_data)

        except Exception as e:
            return jsonify({"message": f"Error occurred: {str(e)}"}), 500

author_bp.add_url_rule("/author/book", view_func=AddBook.as_view('add_book'))





@author_bp.route("/author/event", methods=["GET", "POST"])
class Event(MethodView):
    
    @jwt_required()  
    def get(self):
        try:
            claims = get_jwt()  
            if not (claims.get("is_admin") or claims.get("is_author")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an author to access this resource."
                }), 403

            return AuthorSercices.get_all_events()

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  
    @author_bp.arguments(ReservationRequestSchema)  
    def post(self, request_data):
        """Handle booth reservation requests."""
        try:
            claims = get_jwt() 
            if not (claims.get("is_admin") or claims.get("is_author")):
                return jsonify({
                    "message": "Access denied: You must be either an admin or an author to access this resource."
                }), 403

            return AuthorSercices.post_booth_request(request_data)

        except Exception as e:
            return jsonify({"message": f"Error occurred: {str(e)}"}), 500