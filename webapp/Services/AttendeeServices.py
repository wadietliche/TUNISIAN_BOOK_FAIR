from webapp import db
from datetime import timedelta
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author, Book,FairMap
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema
from flask_smorest import abort
from flask import request, jsonify 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from marshmallow import ValidationError
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token,get_jwt





import requests

def fetch_book_from_google_books(book_title):
    try:
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}&key=AIzaSyCcdNKnm3UL-UK2ykcMoHMvwCmoyhHCkoo"
        )
        response_data = response.json()

        # Log the entire response
        print(f"Full API Response for '{book_title}': {response_data}")

        if "items" not in response_data:
            print(f"No items found for book title: {book_title}")
            return None

        book_data = response_data["items"][0]["volumeInfo"]
        print(f"Book data extracted: {book_data}")

        title = book_data.get("title")
        isbn_info = next(
            (identifier["identifier"] for identifier in book_data.get("industryIdentifiers", []) if identifier["type"] == "ISBN_13"),
            None
        )
        published_year = book_data.get("publishedDate", "").split("-")[0]
        publisher = book_data.get("publisher", "Unknown Publisher")
        author_name = book_data.get("authors", ["Unknown Author"])[0]

        return {
            "title": title,
            "isbn": isbn_info,
            "published_year": int(published_year) if published_year.isdigit() else None,
            "publisher": publisher,
            "author_name": author_name,
        }
    except Exception as e:
        print(f"Error fetching book: {e}")
        return None









@staticmethod
def generate_random_password(length=12):
    """Generate a random password."""
    import random
    import string
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@staticmethod
def fetch_author_from_google_books(author_name):
    """Fetch author details from Google Books API."""
    import requests
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"inauthor:{author_name}",
        "key": "AIzaSyCcdNKnm3UL-UK2ykcMoHMvwCmoyhHCkoo" 
    }
    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("items"):
            return data["items"][0]["volumeInfo"]["authors"][0] 
    return None



def attendeeSignUp(attendee_data):  
    try:
        existing_attendee = Attendee.query.filter_by(attendee_name=attendee_data['attendee_name']).first()
        if existing_attendee:
            abort(400, message="Attendee with this name already exists.")
        
        attendee_data['password'] = generate_password_hash(attendee_data['password'])
        
        attendee = Attendee(**attendee_data)
        
        try:
            db.session.add(attendee)
            db.session.commit()
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
        abort(400, message=err.messages)



def attendeeLogin(login_data):
    try:
        attendee = Attendee.query.filter_by(attendee_name=login_data['attendee_name']).first()
        
        if attendee and check_password_hash(attendee.password, login_data['password']):
            additional_claims = {
                "is_attendee": True,
                "attendee_id": attendee.attendee_id
            }
            access_token = create_access_token(identity=str(attendee.attendee_id), additional_claims=additional_claims, expires_delta=timedelta(minutes=15))
            refresh_token = create_refresh_token(identity=str(attendee.attendee_id))

            
            return jsonify({"message": "Login successful", 
                            "attendee_id": attendee.attendee_id,
                            "tokens":{"access":access_token
                                      }}), 200        
        abort(401, message="Invalid credentials")
    except Exception as e:
        abort(500, message=f"An error occurred during login: {str(e)}")




def add_favorite_book(favorite_book_data):
    try:
        attendee_id = favorite_book_data['attendee_id']
        book_title = favorite_book_data['book_title']
        book = Book.query.filter_by(title=book_title).first()

        if not book:
            fetched_book_details = fetch_book_from_google_books(book_title)

            if not fetched_book_details:
                return {"message": "Book not found in Google Books API."}, 404
            if not fetched_book_details["isbn"]:
                return {"message": "ISBN not found for this book in Google Books API."}, 404
            fetched_title = fetched_book_details['title']
            fetched_isbn = fetched_book_details['isbn']
            fetched_published_year = fetched_book_details.get('published_year')
            fetched_publisher = fetched_book_details.get('publisher')
            fetched_author_name = fetched_book_details['author_name']
            author = Author.query.filter_by(author_name=fetched_author_name).first()

            if not author:
                random_password = generate_random_password()
                print(f"Generated password for author '{fetched_author_name}': {random_password}")

                base_username = fetched_author_name.replace(" ", "_").lower()
                username = base_username
                counter = 1

                while Author.query.filter_by(username=username).first():
                    username = f"{base_username}_{counter}"
                    counter += 1

                author = Author(
                    author_name=fetched_author_name,
                    username=username,
                    password=random_password,
                    approved=False
                )
                db.session.add(author)
                db.session.commit()
                print(f"New author created: {author}")

            book = Book(
                title=fetched_title,
                isbn=fetched_isbn,
                published_year=fetched_published_year,
                publisher=fetched_publisher,
                author_id=author.author_id
            )
            db.session.add(book)
            db.session.commit()
            print(f"New book added: {book}")
        
        # Check for existing favorite
        existing_favorite = FavoriteBook.query.filter_by(book_id=book.book_id, attendee_id=attendee_id).first()

        if existing_favorite:
            return {"message": "This book is already in your favorites."}, 400

        favorite_book = FavoriteBook(book_id=book.book_id, attendee_id=attendee_id)
        db.session.add(favorite_book)
        db.session.commit()

        print(f"Successfully added book '{book.title}' to favorites.")
        return {"message": "Book added to favorites successfully."}, 201

    except ValidationError as ve:
        return {"message": "Invalid data.", "errors": ve.messages}, 422

    except SQLAlchemyError as se:
        # Rollback in case of an error
        db.session.rollback()

        # Handle IntegrityError specifically
        if 'UNIQUE constraint failed' in str(se):
            return {"message": "This book already exists in the database based on its ISBN."}, 400
        return {"message": f"Database error: {str(se)}"}, 500

    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}"}, 500





from flask import current_app

def combinedSearch(query, max_results=5):
    search_url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key=AIzaSyCcdNKnm3UL-'
    try:
        response = requests.get(search_url)
        response.raise_for_status() 
        data = response.json()
        if 'items' in data:
            books = []
            for item in data['items']:
                book_info = item.get('volumeInfo', {})
                books.append({
                    'title': book_info.get('title', 'N/A'),
                    'authors': book_info.get('authors', ['N/A']),
                    'publisher': book_info.get('publisher', 'N/A'),
                    'publishedDate': book_info.get('publishedDate', 'N/A'),
                    'description': book_info.get('description', 'No description available'),
                    'isbn': next((identifier['identifier'] for identifier in book_info.get('industryIdentifiers', []) if identifier['type'] == 'ISBN_13'), 'N/A'),
                    'imageLinks': book_info.get('imageLinks', {}).get('thumbnail', 'N/A'),
                    'previewLink': book_info.get('infoLink', 'N/A')
                })
            return jsonify(books) 
        else:
            return jsonify({"message": "No books found matching the query."})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)})





def add_favorite_author(favorite_author_data):
    try:
        attendee_id = favorite_author_data['attendee_id']
        author_name = favorite_author_data['author_name'].strip()
        author = Author.query.filter(Author.author_name.ilike(author_name)).first()

        if not author:

            fetched_author_name = fetch_author_from_google_books(author_name)

            if not fetched_author_name:
                return {"message": "Author not found in Google Books API."}, 404


            random_password = generate_random_password()
            print(f"Generated password for author '{fetched_author_name}': {random_password}")

            base_username = fetched_author_name.replace(" ", "_").lower()
            username = base_username
            counter = 1
            while Author.query.filter_by(username=username).first():
                username = f"{base_username}_{counter}"
                counter += 1

            author = Author(
                author_name=fetched_author_name,
                username=username,
                password=random_password,
                approved=False
            )
            db.session.add(author)
            db.session.commit()  
            print(f"New author created: {author}")

        existing_favorite = FavoriteAuthor.query.filter_by(author_id=author.author_id, attendee_id=attendee_id).first()

        if existing_favorite:
            return {"message": f"The author '{author.author_name}' is already in your favorites."}, 400
        favorite_author = FavoriteAuthor(author_id=author.author_id, attendee_id=attendee_id)
        db.session.add(favorite_author)
        db.session.commit()
        print(f"Successfully added author '{author.author_name}' to favorites.")
        return {"message": "Author added to favorites successfully."}, 201
    except ValidationError as ve:
        return {"message": "Invalid data.", "errors": ve.messages}, 422
    except SQLAlchemyError as se:
        db.session.rollback() 
        return {"message": f"Database error: {str(se)}"}, 500
    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}"}, 500





def checkAuthorAttendence(author_id):
    author = Author.query.get_or_404(author_id)
    present_event = PresentEvent.query.filter_by(author_id=author_id).first()
    if present_event:
        event = Event.query.get(present_event.event_id)
        return {"message": f"Author is attending the event '{event.event_name}'. Booth: {event.location}"}
    return {"message": "Author is not attending any event."}



def getEventInfo(event_id):
        try:
            event = Event.query.filter_by(event_id=event_id).first()

            if not event:
                return jsonify({"message": "Event not found"}), 404

            event_data = {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "location": event.location,
                "duration": event.duration,
                "start_hour": str(event.start_hour),
                "final_hour": str(event.final_hour)
            }

            return jsonify(event_data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

def getAuthorBooths():
        try:
            approved_booths = (
                FairMap.query
                .join(Author, FairMap.author_id == Author.author_id)
                .filter(FairMap.status == 'approved')
                .add_columns(Author.author_name, FairMap.booth_reference)
                .all()
            )

            if not approved_booths:
                return jsonify({"message": "No approved booths found."}), 404
            data = [
                {
                    "author_name": booth.author_name,
                    "booth_reference": booth.booth_reference
                }
                for booth in approved_booths
            ]

            return jsonify({"approved_authors_booths": data}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


def getAuthorBoothByName():
        try:
            data = request.json
            author_name = data.get('author_name')

            if not author_name:
                return jsonify({
                    "message": "author_name is required."
                }), 400
            author = Author.query.filter_by(author_name=author_name).first()

            if not author:
                return jsonify({
                    "message": f"No author found with the name {author_name}."
                }), 404
            fair_map = FairMap.query.filter_by(author_id=author.author_id).first()

            if not fair_map:
                return jsonify({
                    "message": f"No booth found for author {author_name}."
                }), 404
            if fair_map.status == 'approved':
                return jsonify({
                    "author_name": author.author_name,
                    "booth_reference": fair_map.booth_reference
                }), 200
            else:
                return jsonify({
                    "author_name": author.author_name,
                    "message": "Booth is not approved yet."
                }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


def post(self, event_id):
        try:
            data = request.json
            attendee_id = data.get('attendee_id')
            feedback = data.get('feedback')
            if not attendee_id:
                return jsonify({"message": "attendee_id is required."}), 400
            attendee = Attendee.query.get(attendee_id)
            if not attendee:
                return jsonify({"message": "Attendee not found."}), 404
            event = Event.query.get(event_id)
            if not event:
                return jsonify({"message": "Event not found."}), 404
            existing_attendance = PresentEvent.query.filter_by(author_id=attendee_id, event_id=event_id).first()
            if existing_attendance:
                return jsonify({"message": "Attendance already confirmed."}), 400
            new_attendance = PresentEvent(
                author_id=attendee_id,
                event_id=event_id,
                feedback=feedback  
            )
            db.session.add(new_attendance)
            db.session.commit()

            return jsonify({
                "message": "Attendance confirmed successfully.",
                "attendee_id": attendee_id,
                "event_id": event_id,
                "feedback": feedback if feedback else "No feedback provided"
            }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


def ConfirmAttendence(event_id):
    try:
            data = request.json
            attendee_id = data.get('attendee_id') 
            feedback = data.get('feedback') 
            if not attendee_id:
                return jsonify({"message": "attendee_id is required."}), 400
            attendee = Attendee.query.get(attendee_id)
            if not attendee:
                return jsonify({"message": "Attendee not found."}), 404
            event = Event.query.get(event_id)
            if not event:
                return jsonify({"message": "Event not found."}), 404
            existing_attendance = PresentEvent.query.filter_by(author_id=attendee_id, event_id=event_id).first()
            if existing_attendance:
                return jsonify({"message": "Attendance already confirmed."}), 400
            new_attendance = PresentEvent(
                author_id=attendee_id,
                event_id=event_id,
                feedback=feedback  
            )
            db.session.add(new_attendance)
            db.session.commit()
            return jsonify({
                "message": "Attendance confirmed successfully.",
                "attendee_id": attendee_id,
                "event_id": event_id,
                "feedback": feedback if feedback else "No feedback provided"
            }), 201

    except Exception as e:
            return jsonify({"error": str(e)}), 500
    


def giveFeedback(event_id):
    try:
            data = request.json
            attendee_id = data.get('attendee_id')
            feedback = data.get('feedback')

            if not attendee_id or not feedback:
                return jsonify({
                    "message": "Both attendee_id and feedback are required."
                }), 400
            present_event = PresentEvent.query.filter_by(author_id=attendee_id, event_id=event_id).first()

            if not present_event:
                return jsonify({
                    "message": "No attendance record found for this attendee at this event."
                }), 404
            present_event.feedback = feedback
            db.session.commit()

            return jsonify({
                "message": "Feedback has been updated successfully.",
                "attendee_id": attendee_id,
                "event_id": event_id,
                "feedback": feedback
            }), 200

    except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500