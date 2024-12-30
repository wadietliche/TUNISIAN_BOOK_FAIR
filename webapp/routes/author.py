from flask import Blueprint, request, jsonify, abort
from flask.views import MethodView
from webapp import db
from webapp.models import Author, Book, FairMap, PresentEvent, Event
from webapp.schemas import AuthorSchema, BookSchema
from sqlalchemy.exc import SQLAlchemyError

author_bp = Blueprint("authors", __name__, description="Operations related to Authors")

@author_bp.route("/author/signup", methods=["POST"])
class AuthorSignup(MethodView):
    def post(self):
        author_data = request.get_json()
        # Validate input data using AuthorSchema
        try:
            author_schema = AuthorSchema()
            author_data = author_schema.load(author_data)

            # Check if the username already exists
            if Author.query.filter_by(username=author_data["username"]).first():
                return {"message": "Username already taken"}, 400

            # Create a new author with 'approved' set to False (pending approval)
            new_author = Author(
                author_name=author_data["author_name"],
                username=author_data["username"],
                password=author_data["password"],
                approved=False  # Default status is False (pending approval)
            )

            db.session.add(new_author)
            db.session.commit()

            return {"message": "Sign-up successful. Awaiting admin approval."}, 201

        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500


# Route for author login
@author_bp.route("/author/login", methods=["POST"])
class AuthorLogin(MethodView):
    def post(self):
        login_data = request.get_json()
        username = login_data["username"]
        password = login_data["password"]

        # Find the author by username
        author = Author.query.filter_by(username=username).first()

        if author and author.password == password:
            if author.approved:
                return {"message": "Login successful"}, 200
            else:
                return {"message": "Your account is pending approval. Please wait for admin approval."}, 403
        else:
            return {"message": "Invalid username or password"}, 400

# Route to add a new book
@author_bp.route("/author/book", methods=["POST"])
class AddBook(MethodView):
    @author_bp.arguments(BookSchema)
    def post(self, book_data):
        """Add a new book to the system."""
        author_id = book_data['author_id']
        book_name = book_data['book_name']
        
        author = Author.query.get(author_id)
        
        if not author:
            abort(404, message="Author not found.")
        
        book = Book(**book_data)
        try:
            db.session.add(book)
            db.session.commit()
            return jsonify({"message": "Book added successfully."}), 201
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while adding the book.")

# Route to send a reservation request for an event
@author_bp.route("/author/reservation", methods=["POST"])
class ReservationRequest(MethodView):
    def post(self):
        """Send a reservation request for an event."""
        author_id = request.json.get("author_id")
        event_id = request.json.get("event_id")
        
        author = Author.query.get(author_id)
        event = Event.query.get(event_id)
        
        if not author or not event:
            abort(404, message="Author or event not found.")
        
        # Create a PresentEvent to link author and event
        present_event = PresentEvent(author_id=author_id, event_id=event_id)
        try:
            db.session.add(present_event)
            db.session.commit()
            return jsonify({"message": "Reservation request sent successfully."}), 201
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while sending the reservation.")
