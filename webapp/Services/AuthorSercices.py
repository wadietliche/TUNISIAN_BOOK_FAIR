from flask import Blueprint, request, jsonify
from flask_smorest import  abort
from webapp import db
from webapp.models import Author, Book, FairMap, PresentEvent, Event
from webapp.schemas import AuthorSchema, BookSchema, ReservationRequestSchema,AuthorLoginSchema
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
import uuid




def generate_booth_reference():
    return str(uuid.uuid4())  # or any other method for generating a booth reference



def authorSignUp():
    author_data = request.get_json()

    try:
        # Validate input data using AuthorSchema
        author_schema = AuthorSchema()
        author_data = author_schema.load(author_data)

        # Check if the username already exists
        if Author.query.filter_by(username=author_data["username"]).first():
            return {"message": "Username already taken"}, 400

        # Hash the password before saving it to the database
        author_data["password"] = generate_password_hash(author_data["password"])

        # Create a new author with 'approved' set to False by default
        new_author = Author(
            author_name=author_data["author_name"],
            username=author_data["username"],
            password=author_data["password"],
            approved=False  # Default status is False (pending approval)
        )

        db.session.add(new_author)
        db.session.commit()

        return {"message": "Sign-up successful. Awaiting admin approval."}, 201

    except ValidationError as e:
        # Handle schema validation errors
        return {"message": str(e)}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": str(e)}, 500
    


def authorLogin(login_data):
    try:
        # Validate input data using the schema
        # You no longer need to reload the data here since it's passed as a parameter
        author = Author.query.filter_by(username=login_data['username']).first()

        # Check if the author exists and the password is correct
        if author and check_password_hash(author.password, login_data['password']):

            # Check if the account is approved
            if author.approved:
                # Generate JWT tokens
                access_token = create_access_token(identity=author.username)
                refresh_token = create_refresh_token(identity=author.username)

                # Return the response with tokens
                return jsonify({
                    "message": "Login successful",
                    "author_id": author.author_id,
                    "tokens": {
                        "access": access_token,
                        "refresh": refresh_token
                    }
                }), 200
            else:
                abort(403, message="Your account is pending approval. Please wait for admin approval.")

        # If the credentials are invalid
        abort(401, message="Invalid username or password")

    except Exception as e:
        # Catch any unexpected errors
        abort(500, message=f"An error occurred during login: {str(e)}")
    


def addBookByAuthor(book_data):
    """Add a new book to the system."""
    author_id = book_data['author_id']
    title= book_data['title']
    
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"message": "Author not found."}), 404

    book = Book(**book_data)
    try:
        db.session.add(book)
        db.session.commit()
        return jsonify({"message": "Book added successfully."}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred while adding the book: {str(e)}"}), 500



def reservationRequest():
    """Send a reservation request for an event."""
        # Load and validate the request data using the schema
    try:
        data = ReservationRequestSchema().load(request.json)
    except ValidationError as err:
            abort(400, message=err.messages)  # Return validation errors if any
        
    author_id = data["author_id"]
    event_id = data["event_id"]
        
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




def get_all_events():
    try:
        # Query all events
        events = Event.query.all()

        # Convert the result to a list of dictionaries
        events_list = []
        for event in events:
            events_list.append({
                
                "event_name": event.event_name,
                "location": event.location,
                "duration": event.duration,
                "start_hour": event.start_hour.strftime('%H:%M:%S'),
                "final_hour": event.final_hour.strftime('%H:%M:%S')
            })

        # Return the list as JSON
        return jsonify(events_list), 200
    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500
    



def post_booth_request(request_data):
    fair_map_schema = ReservationRequestSchema()
    try:
        # Extract author_id from the request data
        author_id = request_data.get('author_id')  # Using .get to access dictionary values

        # Check if the author already has a booth request
        existing_request = FairMap.query.filter_by(author_id=author_id).first()

        if existing_request:
            if existing_request.status == 'pending':
                # Author has a pending request
                return jsonify({
                    "message": "We are processing your request. Thank you for your patience."
                }), 200
            elif existing_request.status == 'approved':
                # Author has been approved
                return jsonify({
                    "message": "You are approved and assigned to a booth.",
                    "booth_reference": existing_request.booth_reference
                }), 200

        # Prepare data, excluding booth_reference
        data = {"author_id": author_id}

        # Validate data using the schema
        validated_data = fair_map_schema.load(data)

        # Manually add the booth_reference field here, as it is not part of the schema
        validated_data["booth_reference"] = generate_booth_reference()

        # Create a new booth request
        new_request = FairMap(**validated_data)
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "message": "Your request has been submitted and is pending approval."
        }), 201

    except ValidationError as ve:
        # Handle validation errors
        return jsonify({
            "error": "Validation error",
            "details": ve.messages
        }), 400

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            "error": str(e)
        }), 500
    


