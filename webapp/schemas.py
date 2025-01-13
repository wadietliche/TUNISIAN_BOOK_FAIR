from marshmallow import Schema, fields, validate, ValidationError


class AdminSchema(Schema):
    admin_id = fields.Int(dump_only=True)  
    admin_name = fields.Str(required=True)
    password = fields.Str(required=True)

class AdminLoginSchema(Schema):
    admin_name = fields.Str(required=True)  # Admin name is required
    password = fields.Str(required=True)    # Password is required

class AttendeeSchema(Schema):
    attendee_id = fields.Int(dump_only=True)
    attendee_name = fields.Str(required=True)
    password = fields.Str(required=True)

class AttendeeLoginSchema(Schema):
    attendee_name = fields.Str(required=True)
    password = fields.Str(required=True)

class FavoriteAuthorSchema(Schema):
    favorite_author_id = fields.Int(dump_only=True)
    author_name = fields.Str(required=True)  # Expecting a string name
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
    author_name = fields.Str(required=True)  # Author's full name
    username = fields.Str(required=True)    # Author's unique username
    password = fields.Str(required=True)    # Author's password

# Schema to handle login data for authors
class AuthorLoginSchema(Schema):
    username = fields.Str(required=True)    # Author's unique username
    password = fields.Str(required=True,validate=validate.Length(min=1))    # Author's password

# Schema to handle book data
class BookSchema(Schema):
    book_id = fields.Int(dump_only=True)
    isbn = fields.Str(required=True)  # Add ISBN as a required field
    title = fields.Str(required=True)
    author_id = fields.Int(required=True)
    published_year = fields.Int()
    publisher = fields.Str()

class CombinedSearchSchema(Schema):
    title = fields.String(required=False, description="Title of the book to search for.")
    author_name = fields.String(required=False, description="Author name of the book to search for.")


class ReservationRequestSchema(Schema):
    author_id = fields.Int(required=True)
    event_id = fields.Int(required=True)

class AuthorApprovalSchema(Schema):
    approve = fields.Bool(required=True, error_messages={"required": "Approval flag is required."})



class RecommendationRequestSchema(Schema):
    attendee_id = fields.Int(required=True)

class RecommendationResponseSchema(Schema):
    recommended_books = fields.List(fields.Nested(BookSchema)) 