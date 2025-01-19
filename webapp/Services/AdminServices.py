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
        admin_schema = AdminSchema()
        validated_data = admin_schema.load(admin_data)  
        existing_admin = Admin.query.filter_by(admin_name=validated_data['admin_name']).first()
        if existing_admin:
            return jsonify({"message": "An admin with this name already exists."}), 400
        validated_data['password'] = generate_password_hash(validated_data['password'])

        admin = Admin(**validated_data)
        db.session.add(admin) 
        db.session.commit()  
        return jsonify({
            "message": "Admin created successfully.",
            "admin": {
                "admin_id": admin.admin_id,
                "admin_name": admin.admin_name
            }
        }), 201

    except IntegrityError:
        db.session.rollback()  
        return jsonify({"message": "An admin with this name already exists."}), 400
    
    except SQLAlchemyError as e:
        db.session.rollback()  
        return jsonify({"message": f"An error occurred while processing your request: {str(e)}"}), 500
    
    except ValidationError as err:
        return jsonify({"message": err.messages}), 400 





def adminLogin(login_data):
    try:
        admin = Admin.query.filter_by(admin_name=login_data['admin_name']).first()

        if admin and check_password_hash(admin.password, login_data['password']):
            additional_claims = {
                "is_admin": True,
                "admin_id": admin.admin_id
            }
            access_token = create_access_token(identity=admin.admin_name,additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=admin.admin_name)
            return jsonify({
                "message": "Login successful",
                "admin_id": admin.admin_id,
                "tokens": {
                    "access": access_token,
                }
            }), 200

        abort(401, message="Invalid credentials")

    except Exception as e:
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
    author = Author.query.get_or_404(author_id)
    author.approved = True
    db.session.commit()
    return {"message": f"Author {author.author_name} has been approved."}, 200


def create_event(event_data):
    try:
        existing_event = Event.query.filter_by(event_name=event_data["event_name"]).first()
        
        if existing_event:
            return {"message": "Event with this name already exists."}, 409  

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
        return {"message": "Event created successfully!"}, 201  
    except Exception as e:
        db.session.rollback()
        return {"message": str(e)}, 500  


        



def approve_and_assign_booth(author_id, booth_reference):
    fair_map_schema = FairMapSchema2()
    try:
        data = {"author_id": author_id, "booth_reference": booth_reference, "status": "approved"}
        validated_data = fair_map_schema.load(data)
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

        existing_booth = FairMap.query.filter_by(booth_reference=validated_data["booth_reference"]).first()
        if existing_booth:
            return jsonify({
                "message": f"The booth '{validated_data['booth_reference']}' is already assigned to another author."
            }), 400

        booth_request.status = validated_data["status"]
        booth_request.booth_reference = validated_data["booth_reference"]
        db.session.commit()

        return jsonify({
            "message": "The request has been approved and the booth has been assigned.",
            "author_id": booth_request.author_id,
            "booth_reference": booth_request.booth_reference
        }), 200

    except ValidationError as ve:
        return jsonify({
            "error": "Validation error",
            "details": ve.messages
        }), 400

    except Exception as e:
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

            attendee = Attendee.query.filter_by(attendee_id=attendee_id).first()
            if not attendee:
                return jsonify({
                    "message": "Attendee not found."
                }), 404

            FavoriteBook.query.filter_by(attendee_id=attendee_id).delete()

            FavoriteAuthor.query.filter_by(attendee_id=attendee_id).delete()

            db.session.delete(attendee)
            db.session.commit()

            return jsonify({
                "message": f"Attendee with ID {attendee_id} and associated data have been deleted successfully."
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


def banAuthor():
        try:
            data = request.json
            author_id = data.get('author_id')

            if not author_id:
                return jsonify({"message": "author_id is required."}), 400

            author = Author.query.filter_by(author_id=author_id).first()

            if not author:
                return jsonify({"message": "Author not found."}), 404
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
        attendees = db.session.query(Attendee.attendee_id, Attendee.attendee_name).all()
        result = [{"attendee_id": attendee.attendee_id, "attendee_name": attendee.attendee_name} for attendee in attendees]
        
        return result
    except Exception as e:
        print(f"An error occurred while fetching attendees: {e}")
        return []



def get_all_authors():
        try:
            authors = db.session.query(Author.author_id, Author.author_name, Author.approved).all()
            author_list = [
                {"author_id": author_id, "author_name": author_name, "approved": approved} 
                for author_id, author_name, approved in authors
            ]
            
            return {"authors": author_list}, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
        


def delete_event(event_id):
    try:
        event = Event.query.get(event_id)
        
        if not event:
            return {"message": "Event not found."}, 404  
        db.session.delete(event)
        db.session.commit()

        return {"message": "Event deleted successfully!"}, 200  
    
    except Exception as e:
        db.session.rollback()
        return {"message": f"An error occurred: {str(e)}"}, 500  