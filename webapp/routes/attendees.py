from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema
from werkzeug.security import generate_password_hash, check_password_hash

attendee_bp = Blueprint("Attendees", "attendees", description="Operations on Attendees")

# Attendee Sign-up (POST request to create a new attendee)
@attendee_bp.route("/attendee/signup")
class AttendeeSignup(MethodView):
    @attendee_bp.arguments(AttendeeSchema)
    @attendee_bp.response(201, AttendeeSchema)
    def post(self, attendee_data):
        # Hash the password before saving
        attendee_data['password'] = generate_password_hash(attendee_data['password'])
        attendee = Attendee(**attendee_data)
        
        try:
            db.session.add(attendee)
            db.session.commit()
            return attendee
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Attendee with this name already exists.")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred during sign-up.")

# Attendee Login (POST request to authenticate)
@attendee_bp.route("/attendee/login")
class AttendeeLogin(MethodView):
    @attendee_bp.arguments(AttendeeLoginSchema)
    def post(self, login_data):
        attendee = Attendee.query.filter_by(attendee_name=login_data['attendee_name']).first()
        if attendee and check_password_hash(attendee.password, login_data['password']):
            return {"message": "Login successful", "attendee_id": attendee.attendee_id}
        abort(401, message="Invalid credentials")

# Add to Favorite Books (POST request to mark a book as favorite)
@attendee_bp.route("/attendee/favorite/book")
class AddFavoriteBook(MethodView):
    @attendee_bp.arguments(FavoriteBookSchema)
    def post(self, favorite_book_data):
        favorite_book = FavoriteBook(**favorite_book_data)
        try:
            db.session.add(favorite_book)
            db.session.commit()
            return {"message": "Book added to favorites."}, 201
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while adding the book.")

# Add to Favorite Authors (POST request to mark an author as favorite)
attendee_bp.route("/attendee/favorite/author", methods=["POST"])
class AddFavoriteAuthor(MethodView):
    @attendee_bp.arguments(FavoriteAuthorSchema)
    def post(self, favorite_author_data):
        # Extract the author name from the incoming request data
        author_name = favorite_author_data['author_name']
        attendee_id = favorite_author_data['attendee_id']
        
        # Search for the author by name
        author = Author.query.filter_by(author_name=author_name).first()
        
        if not author:
            # Return an error if the author is not found
            return {"message": "Author not found."}, 404
        
        # Create a new FavoriteAuthor entry linking the attendee to the author
        favorite_author = FavoriteAuthor(author_id=author.author_id, attendee_id=attendee_id)
        
        try:
            # Add the new favorite author to the session and commit
            db.session.add(favorite_author)
            db.session.commit()
            return {"message": "Author added to favorites."}, 201
        except SQLAlchemyError:
            # Handle any SQLAlchemy errors, such as database issues
            db.session.rollback()
            return {"message": "An error occurred while adding the author to favorites."}, 500

# Check if Author is Attending (GET request to check if an author is attending an event)
@attendee_bp.route("/attendee/author/<int:author_id>/attending")
class CheckAuthorAttendance(MethodView):
    def get(self, author_id):
        author = Author.query.get_or_404(author_id)
        present_event = PresentEvent.query.filter_by(author_id=author_id).first()
        if present_event:
            event = Event.query.get(present_event.event_id)
            return {"message": f"Author is attending the event '{event.event_name}'. Booth: {event.location}"}
        return {"message": "Author is not attending any event."}

# Attend an Event (POST request to mark attendance)
@attendee_bp.route("/attendee/event/attend")
class AttendEvent(MethodView):
    @attendee_bp.arguments(EventAttendanceSchema)
    def post(self, attendance_data):
        event = Event.query.get_or_404(attendance_data['event_id'])
        attendee = Attendee.query.get_or_404(attendance_data['attendee_id'])
        
        # Check if the attendee is already attending the event
        present_event = PresentEvent.query.filter_by(author_id=attendee.attendee_id, event_id=event.event_id).first()
        if not present_event:
            # Create a new attendance record
            new_event = PresentEvent(**attendance_data)
            db.session.add(new_event)
            db.session.commit()
            return {"message": f"Attendee successfully attending event '{event.event_name}'."}
        return {"message": "Attendee is already attending this event."}
