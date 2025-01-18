from flask_smorest import abort
from flask import jsonify,request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity,get_jwt
import logging
from datetime import datetime
from webapp import db
from webapp.models import Admin, Author, Event, FairMap,Attendee,FavoriteBook,FavoriteAuthor
from webapp.schemas import AdminSchema, AdminLoginSchema, EventSchema, FairMapSchema2



def createNewAdmin(admin_data):
    """Create a new admin while strictly adhering to the AdminSchema."""
    try:
        # Validate the incoming data using the AdminSchema
        admin_schema = AdminSchema()
        # This will raise a ValidationError if the data does not match the schema
        validated_data = admin_schema.load(admin_data)  

        # Check if an admin with the same name already exists
        existing_admin = Admin.query.filter_by(admin_name=validated_data['admin_name']).first()
        if existing_admin:
            return jsonify({"message": "An admin with this name already exists."}), 400
        
        # Hash the password before storing it
        validated_data['password'] = generate_password_hash(validated_data['password'])
        
        # Create Admin from validated admin_data
        admin = Admin(**validated_data)
        db.session.add(admin)  # Add the new Admin to the session
        db.session.commit()  # Commit the transaction
        
        # Return success message with admin details
        return jsonify({
            "message": "Admin created successfully.",
            "admin": {
                "admin_id": admin.admin_id,
                "admin_name": admin.admin_name
            }
        }), 201

    except IntegrityError:
        # Handle integrity errors (e.g., duplicate admin name)
        db.session.rollback()  # Rollback the session to avoid partial commits
        return jsonify({"message": "An admin with this name already exists."}), 400
    
    except SQLAlchemyError as e:
        # Handle other SQLAlchemy errors (e.g., database connection issues)
        db.session.rollback()  
        return jsonify({"message": f"An error occurred while processing your request: {str(e)}"}), 500
    
    except ValidationError as err:
        # Handle validation errors if any (e.g., required fields missing)
        return jsonify({"message": err.messages}), 400  # Return validation errors if any





def adminLogin(login_data):
    try:
        # Retrieve the admin from the database using the admin_name
        admin = Admin.query.filter_by(admin_name=login_data['admin_name']).first()

        # Check if admin exists and password is correct
        if admin and check_password_hash(admin.password, login_data['password']):
            additional_claims = {
                "is_admin": True,
                "admin_id": admin.admin_id
            }
            # Generate access and refresh tokens
            access_token = create_access_token(identity=admin.admin_name,additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=admin.admin_name)
            return jsonify({
                "message": "Login successful",
                "admin_id": admin.admin_id,
                "tokens": {
                    "access": access_token,
                    #"refresh": refresh_token
                    
                }
            }), 200

        # Abort with error if credentials are invalid
        abort(401, message="Invalid credentials")

    except Exception as e:
        # Log any exception and return a 500 error
        logging.error(f"Unexpected error: {str(e)}")
        abort(500, message=f"An error occurred during login: {str(e)}")





def getAdminById(admin_id):
    admin = Admin.query.get_or_404(admin_id)
    return {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name
    }



def delAdminById(admin_id):
    """Delete an admin by ID."""
    admin = Admin.query.get_or_404(admin_id)
    db.session.delete(admin)
    db.session.commit()
    return {"message": "Admin deleted"}, 200





def returnAllAdmins():
    admins = Admin.query.all()
    return [
            {"admin_id": admin.admin_id, "admin_name": admin.admin_name}
            for admin in admins
        ]




def approveAuthor(author_id):
    # Query the author by their ID, if not found, an error will be raised
    author = Author.query.get_or_404(author_id)
    
    # Set the 'approved' flag to True to approve the author
    author.approved = True
    
    # Commit the changes to the database
    db.session.commit()

    # Return a success message and HTTP status code 200 (OK)
    return {"message": f"Author {author.author_name} has been approved."}, 200


def create_event(event_data):
    try:
        # Check if the event already exists (using event_name, or any unique field)
        existing_event = Event.query.filter_by(event_name=event_data["event_name"]).first()
        
        if existing_event:
            return {"message": "Event with this name already exists."}, 409  # Conflict status code

        # Parse times into datetime.time objects
        start_hour = datetime.strptime(event_data["start_hour"], "%H:%M:%S").time()
        final_hour = datetime.strptime(event_data["final_hour"], "%H:%M:%S").time()
        
        # Create the new event
        event = Event(
            event_name=event_data["event_name"],
            location=event_data["location"],
            duration=event_data["duration"],
            start_hour=start_hour,
            final_hour=final_hour,
        )
        db.session.add(event)
        db.session.commit()
        return {"message": "Event created successfully!"}, 201  # Created status code
    except Exception as e:
        db.session.rollback()
        return {"message": str(e)}, 500  # Internal server error


        



def approve_and_assign_booth(author_id, booth_reference):
    fair_map_schema = FairMapSchema2()
    try:
        # Validate the input using the schema
        data = {"author_id": author_id, "booth_reference": booth_reference, "status": "approved"}
        validated_data = fair_map_schema.load(data)

        # Fetch the booth request for the given author_id
        booth_request = FairMap.query.filter_by(author_id=validated_data["author_id"]).first()

        if not booth_request:
            return jsonify({
                "message": "No booth request found for this author."
            }), 404

        if booth_request.status == 'approved':
            return jsonify({
                "message": "This request has already been approved.",
                "booth_reference": booth_request.booth_reference
            }), 200

        # Check if the booth_reference is already assigned
        existing_booth = FairMap.query.filter_by(booth_reference=validated_data["booth_reference"]).first()
        if existing_booth:
            return jsonify({
                "message": f"The booth '{validated_data['booth_reference']}' is already assigned to another author."
            }), 400

        # Approve the request and assign the booth
        booth_request.status = validated_data["status"]
        booth_request.booth_reference = validated_data["booth_reference"]
        db.session.commit()

        return jsonify({
            "message": "The request has been approved and the booth has been assigned.",
            "author_id": booth_request.author_id,
            "booth_reference": booth_request.booth_reference
        }), 200

    except ValidationError as ve:
        # Handle validation errors
        return jsonify({
            "error": "Validation error",
            "details": ve.messages
        }), 400

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "error": str(e)
        }), 500
    


def deleteAttendee():
        try:
            data = request.json
            attendee_id = data.get('attendee_id')

            if not attendee_id:
                return jsonify({
                    "message": "attendee_id is required."
                }), 400
            
            # Fetch the attendee
            attendee = Attendee.query.filter_by(attendee_id=attendee_id).first()
            if not attendee:
                return jsonify({
                    "message": "Attendee not found."
                }), 404
            
            # Step 1: Delete associated FavoriteBook entries
            FavoriteBook.query.filter_by(attendee_id=attendee_id).delete()
            
            # Step 2: Delete associated FavoriteAuthor entries
            FavoriteAuthor.query.filter_by(attendee_id=attendee_id).delete()
            
            # Step 3: Delete the Attendee
            db.session.delete(attendee)
            db.session.commit()

            return jsonify({
                "message": f"Attendee with ID {attendee_id} and associated data have been deleted successfully."
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


def banAuthor():
        try:
            # Parse request data
            data = request.json
            author_id = data.get('author_id')

            if not author_id:
                return jsonify({"message": "author_id is required."}), 400
            
            # Find the author
            author = Author.query.filter_by(author_id=author_id).first()

            if not author:
                return jsonify({"message": "Author not found."}), 404
            
            # Update the 'approved' status to False
            author.approved = False
            db.session.commit()

            return jsonify({
                "message": f"Author with ID {author_id} has been banned successfully.",
                "author_id": author_id,
                "author_name": author.author_name
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


def returnClaims():
    claims=get_jwt()
    return{"claims":claims}



def get_attendee_details():
    try:
        # Query the attendee table for attendee_id and attendee_name
        attendees = db.session.query(Attendee.attendee_id, Attendee.attendee_name).all()
        
        # Convert the result to a list of dictionaries
        result = [{"attendee_id": attendee.attendee_id, "attendee_name": attendee.attendee_name} for attendee in attendees]
        
        return result
    except Exception as e:
        print(f"An error occurred while fetching attendees: {e}")
        return []



def get_all_authors():
        try:
            # Query all authors including the 'approved' status
            authors = db.session.query(Author.author_id, Author.author_name, Author.approved).all()
            
            # Convert the query result into a list of dictionaries
            author_list = [
                {"author_id": author_id, "author_name": author_name, "approved": approved} 
                for author_id, author_name, approved in authors
            ]
            
            return {"authors": author_list}, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
        


def delete_event(event_id):
    try:
        # Query the event to see if it exists
        event = Event.query.get(event_id)
        
        if not event:
            return {"message": "Event not found."}, 404  # Not Found status code

        # Delete the event
        db.session.delete(event)
        db.session.commit()

        return {"message": "Event deleted successfully!"}, 200  # OK status code
    
    except Exception as e:
        db.session.rollback()
        return {"message": f"An error occurred: {str(e)}"}, 500  # Internal server error