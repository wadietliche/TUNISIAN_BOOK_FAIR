from marshmallow import Schema, fields, validate


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


class FavoriteBookSchema(Schema):
    book_id = fields.Int(required=True)
    attendee_id = fields.Int(dump_only=True)



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
    book_name = fields.Str(required=True)
    author_id = fields.Int(required=True)
    abstract = fields.Str()
    date_of_release = fields.Date()

class CombinedSearchSchema(Schema):
    title = fields.String(required=False, description="Title of the book to search for.")
    author_name = fields.String(required=False, description="Author name of the book to search for.")


class ReservationRequestSchema(Schema):
    author_id = fields.Int(required=True)
    event_id = fields.Int(required=True)

class AuthorApprovalSchema(Schema):
    approve = fields.Bool(required=True, error_messages={"required": "Approval flag is required."})