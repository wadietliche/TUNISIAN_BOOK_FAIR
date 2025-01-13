from webapp import db
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, PresentEvent, Event, Author, Book,FairMap
from webapp.schemas import AttendeeSchema, AttendeeLoginSchema, FavoriteBookSchema, FavoriteAuthorSchema, EventAttendanceSchema
from flask_smorest import abort
from flask import request, jsonify 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from marshmallow import ValidationError
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token





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
            return data["items"][0]["volumeInfo"]["authors"][0]  # First author
    return None



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

            access_token= create_access_token(identity=attendee.attendee_name)
            refresh_token=create_refresh_token(identity=attendee.attendee_name)
            
            return jsonify({"message": "Login successful", 
                            "attendee_id": attendee.attendee_id,
                            "tokens":{"access":access_token,
                                      "refresh":refresh_token}}), 200        
        abort(401, message="Invalid credentials")
    except Exception as e:
        abort(500, message=f"An error occurred during login: {str(e)}")




def add_favorite_book(favorite_book_data):
    try:
        # Extract attendee ID and book title from the input
        attendee_id = favorite_book_data['attendee_id']
        book_title = favorite_book_data['book_title']

        # Check if the book already exists in the database
        book = Book.query.filter_by(title=book_title).first()

        if not book:
            # If the book doesn't exist, fetch book details from Google Books API
            fetched_book_details = fetch_book_from_google_books(book_title)

            if not fetched_book_details:
                return {"message": "Book not found in Google Books API."}, 404
            if not fetched_book_details["isbn"]:
                return {"message": "ISBN not found for this book in Google Books API."}, 404

            # Extract book details from the fetched data
            fetched_title = fetched_book_details['title']
            fetched_isbn = fetched_book_details['isbn']
            fetched_published_year = fetched_book_details.get('published_year')
            fetched_publisher = fetched_book_details.get('publisher')
            fetched_author_name = fetched_book_details['author_name']

            # Check if the author exists in the database
            author = Author.query.filter_by(author_name=fetched_author_name).first()

            if not author:
                # Add the author to the database if they don't exist
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

            # Add the book to the database
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

        # Check if the book is already in the attendee's favorites
        existing_favorite = FavoriteBook.query.filter_by(book_id=book.book_id, attendee_id=attendee_id).first()

        if existing_favorite:
            return {"message": "This book is already in your favorites."}, 400

        # Add the book to the favorite books table
        favorite_book = FavoriteBook(book_id=book.book_id, attendee_id=attendee_id)
        db.session.add(favorite_book)
        db.session.commit()

        print(f"Successfully added book '{book.title}' to favorites.")
        return {"message": "Book added to favorites successfully."}, 201

    except ValidationError as ve:
        return {"message": "Invalid data.", "errors": ve.messages}, 422

    except SQLAlchemyError as se:
        db.session.rollback()
        return {"message": f"Database error: {str(se)}"}, 500

    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}"}, 500




from flask import current_app

def combinedSearch(query, max_results=5):
    # Prepare the query string to search in title, author, or publisher
    search_url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key=AIzaSyCcdNKnm3UL-UK2ykcMoHMvwCmoyhHCkoo'

    # Perform the request to the Google Books API
    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Will raise an exception for 4xx or 5xx responses
        data = response.json()

        # If the response contains items (books)
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
            return jsonify(books)  # Return the list of books in JSON format
        else:
            return jsonify({"message": "No books found matching the query."})

    except requests.exceptions.RequestException as e:
        # Handle any errors in the request (e.g., network issues)
        return jsonify({"error": str(e)})





def add_favorite_author(favorite_author_data):
    try:
        # Extract attendee ID and author name from the input
        attendee_id = favorite_author_data['attendee_id']
        author_name = favorite_author_data['author_name']

        # Check if the author already exists in the database
        author = Author.query.filter_by(author_name=author_name).first()

        if not author:
            # If the author doesn't exist, fetch author details from Google Books API
            fetched_author_name = fetch_author_from_google_books(author_name)

            if not fetched_author_name:
                return {"message": "Author not found in Google Books API."}, 404

            # Generate a random password for the new author entry
            random_password = generate_random_password()
            print(f"Generated password for author '{fetched_author_name}': {random_password}")

            # Generate a unique username (avoid duplicating usernames)
            base_username = fetched_author_name.replace(" ", "_").lower()
            username = base_username
            counter = 1

            # Check if the username already exists in the database
            while Author.query.filter_by(username=username).first():
                username = f"{base_username}_{counter}"
                counter += 1

            # Add the new author to the database
            author = Author(
                author_name=fetched_author_name,
                username=username,
                password=random_password,
                approved=False
            )
            db.session.add(author)
            db.session.commit()  # Save the new author to the database
            print(f"New author created: {author}")

        # Check if the author is already in the attendee's favorites
        existing_favorite = FavoriteAuthor.query.filter_by(author_id=author.author_id, attendee_id=attendee_id).first()

        if existing_favorite:
            # If the author is already in the favorite list, return a message
            return {"message": "This author is already in your favorites."}, 400

        # Create a new favorite author entry if the author is not already in the favorites
        favorite_author = FavoriteAuthor(author_id=author.author_id, attendee_id=attendee_id)
        db.session.add(favorite_author)
        db.session.commit()

        print(f"Successfully added author '{author.author_name}' to favorites.")
        return {"message": "Author added to favorites successfully."}, 201

    except ValidationError as ve:
        return {"message": "Invalid data.", "errors": ve.messages}, 422

    except SQLAlchemyError as se:
        db.session.rollback()  # Rollback on any database error
        return {"message": f"Database error: {str(se)}"}, 500

    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}"}, 500


    



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



def getEventInfo(event_id):
        try:
            # Fetch the specific event by ID
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
            # Fetch all authors with approved booths
            approved_booths = (
                FairMap.query
                .join(Author, FairMap.author_id == Author.author_id)
                .filter(FairMap.status == 'approved')
                .add_columns(Author.author_name, FairMap.booth_reference)
                .all()
            )

            if not approved_booths:
                return jsonify({"message": "No approved booths found."}), 404

            # Prepare the response data
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