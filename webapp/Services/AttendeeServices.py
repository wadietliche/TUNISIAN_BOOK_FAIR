from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema,BookSearchSchema, AuthorSearchSchema
from flask_smorest import abort
from flask import request, jsonify 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from marshmallow import ValidationError
from flask import jsonify



def attendeeSignUp(attendee_data):  # Add the attendee_data parameter
    try:
        # Check if the attendee_name already exists in the database
        existing_attendee = Attendee.query.filter_by(attendee_name=attendee_data['attendee_name']).first()
        if existing_attendee:
            abort(400, message="Attendee with this name already exists.")
        
        # Hash the password before saving
        attendee_data['password'] = generate_password_hash(attendee_data['password'])
        
        # Create a new Attendee object
        attendee = Attendee(**attendee_data)
        
        try:
            # Add the new attendee to the database
            db.session.add(attendee)
            db.session.commit()
            
            # Return success message along with attendee data
            return jsonify({
                "message": "Sign-up successful. Welcome to the platform!",
                "attendee": AttendeeSchema().dump(attendee)
            }), 201
        except IntegrityError:
            db.session.rollback()
            abort(400, message="An error occurred while processing your sign-up.")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred during sign-up.")
    except ValidationError as err:
        abort(400, message=err.messages)  # Return validation errors if any



def attendeeLogin(login_data):
    try:
        # Validate input data using the schema
        # You no longer need to reload the data here since it's passed as a parameter
        attendee = Attendee.query.filter_by(attendee_name=login_data['attendee_name']).first()
        
        if attendee and check_password_hash(attendee.password, login_data['password']):
            return jsonify({"message": "Login successful", "attendee_id": attendee.attendee_id}), 200
        
        abort(401, message="Invalid credentials")
    except Exception as e:
        abort(500, message=f"An error occurred during login: {str(e)}")




def addFavoriteBook(favorite_book_data):
    favorite_book = FavoriteBook(**favorite_book_data)
    try:
        db.session.add(favorite_book)
        db.session.commit()
        return {"message": "Book added to favorites."}, 201
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="An error occurred while adding the book.")




def bookSearch(search_data):
    title = search_data["title"]
    response = requests.get("https://openlibrary.org/search.json", params={"title": title})
        
    if response.status_code != 200:
        return {"message": "Failed to fetch data from Open Library API."}, 500

    books = [
        {
            "title": book.get("title"),
            "author": ", ".join(book.get("author_name", [])),
            "cover_image": f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-L.jpg" if book.get("cover_i") else None,
            "publish_year": book.get("first_publish_year")
            }
        for book in response.json().get("docs", [])
    ]

    return {"books": books}




def authorSearch(search_data):
    author_name = search_data["author_name"]
    base_url = "https://openlibrary.org/search.json"

    # Fetch books by author
    response = requests.get(base_url, params={"author": author_name})
    if response.status_code != 200:
        return {"message": "Failed to fetch author data from Open Library API."}, 500

    books_data = response.json().get("docs", [])
    books = [
        {
            "title": book.get("title"),
            "author": ", ".join(book.get("author_name", [])),
            "cover_image": f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-L.jpg" if book.get("cover_i") else None,
            "publish_year": book.get("first_publish_year"),
        }
            for book in books_data
    ]

    return jsonify({"books": books})




def addFavoriteAuthor(favorite_author_data):
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
    



def confirmAttendance(attendance_data):
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



def checkAuthorAttendence(author_id):
    author = Author.query.get_or_404(author_id)
    present_event = PresentEvent.query.filter_by(author_id=author_id).first()
    if present_event:
        event = Event.query.get(present_event.event_id)
        return {"message": f"Author is attending the event '{event.event_name}'. Booth: {event.location}"}
    return {"message": "Author is not attending any event."}