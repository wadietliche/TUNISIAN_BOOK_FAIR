from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime



class AdminSchema(Schema):
    admin_id = fields.Int(dump_only=True)  
    admin_name = fields.Str(required=True)
    password = fields.Str(required=True)

class AdminLoginSchema(Schema):
    admin_name = fields.Str(required=True)  
    password = fields.Str(required=True)    

class AttendeeSchema(Schema):
    attendee_id = fields.Int(dump_only=True)
    attendee_name = fields.Str(required=True)
    password = fields.Str(required=True)

class AttendeeLoginSchema(Schema):
    attendee_name = fields.Str(required=True)
    password = fields.Str(required=True)

class FavoriteAuthorSchema(Schema):
    favorite_author_id = fields.Int(dump_only=True)
    author_name = fields.Str(required=True) 
    attendee_id = fields.Int(required=True)


from marshmallow import Schema, fields, validates, ValidationError

class FavoriteBookSchema(Schema):
    attendee_id = fields.Int(required=True, error_messages={"required": "Attendee ID is required."})
    book_title = fields.Str(
        required=True,
        validate=lambda x: len(x) > 0,
        error_messages={"required": "Book title is required.", "validator_failed": "Book title must not be empty."}
    )

    @validates("attendee_id")
    def validate_attendee_id(self, value):
        if value <= 0:
            raise ValidationError("Attendee ID must be a positive integer.")

    @validates("book_title")
    def validate_book_title(self, value):
        if not value.strip():
            raise ValidationError("Book title must not be empty or whitespace.")




class EventAttendanceSchema(Schema):
    event_id = fields.Int(required=True)
    attendee_id = fields.Int(dump_only=True)


class AuthorSchema(Schema):
    author_name = fields.Str(required=True)  
    username = fields.Str(required=True)   
    password = fields.Str(required=True)    


class AuthorLoginSchema(Schema):
    username = fields.Str(required=True)    
    password = fields.Str(required=True,validate=validate.Length(min=1))  


class BookSchema(Schema):
    book_id = fields.Int(dump_only=True)
    isbn = fields.Str(required=True) 
    title = fields.Str(required=True)
    author_id = fields.Int(required=True)
    published_year = fields.Int()
    publisher = fields.Str()

class CombinedSearchSchema(Schema):
    title = fields.String(required=False, description="Title of the book to search for.")
    author_name = fields.String(required=False, description="Author name of the book to search for.")



class AuthorApprovalSchema(Schema):
    approve = fields.Bool(required=True, error_messages={"required": "Approval flag is required."})



class RecommendationRequestSchema(Schema):
    attendee_id = fields.Int(required=True)

class RecommendationResponseSchema(Schema):
    recommended_books = fields.List(fields.Nested(BookSchema)) 



class FairMapSchema(Schema):
    booth_reference = fields.String(required=False)  
    author_id = fields.Integer(required=True)  
    status = fields.String(required=False, dump_only=True) 


class EventSchema(Schema):
    event_name = fields.Str(required=True)
    location = fields.Str(required=True)
    duration = fields.Int(required=True)
    start_hour = fields.Str(required=True)
    final_hour = fields.Str(required=True)

    @validates("start_hour")
    def validate_start_hour(self, value):
        try:
            datetime.strptime(value, "%H:%M:%S").time()
        except ValueError:
            raise ValidationError("Not a valid time. Expected format: HH:MM:SS.")

    @validates("final_hour")
    def validate_final_hour(self, value):
        try:
            datetime.strptime(value, "%H:%M:%S").time()
        except ValueError:
            raise ValidationError("Not a valid time. Expected format: HH:MM:SS.")
        

class FairMapSchema2(Schema):
    booth_reference = fields.String(
        required=True, 
        validate=validate.Length(max=50), 
        error_messages={"required": "Booth reference is required."}
    )
    author_id = fields.Integer(
        required=True, 
        error_messages={"required": "Author ID is required."}
    )
    status = fields.String(
        required=True,
        validate=validate.OneOf(["pending", "approved"]),
        error_messages={
            "required": "Status is required.",
            "invalid": "Status must be 'pending' or 'approved'."
        }
    )

class ReservationRequestSchema(Schema): 
    author_id = fields.Int(required=True)
    event_id = fields.Int(required=False)