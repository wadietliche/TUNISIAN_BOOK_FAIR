from marshmallow import Schema, fields


from marshmallow import Schema, fields

class AdminSchema(Schema):
    admin_id = fields.Int(dump_only=True)  
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
    author_name = fields.Str(required=True)  
    attendee_id = fields.Int(dump_only=True)


class FavoriteBookSchema(Schema):
    book_id = fields.Int(required=True)
    attendee_id = fields.Int(dump_only=True)

class FavoriteAuthorSchema(Schema):
    author_id = fields.Int(required=True)
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
    password = fields.Str(required=True)    # Author's password

# Schema to handle book data
class BookSchema(Schema):
    book_name = fields.Str(required=True)
    author_id = fields.Int(required=True)
    abstract = fields.Str()
    date_of_release = fields.Date()

class BookSearchSchema(Schema):
    title = fields.Str(required=True, error_messages={"required": "Title is required to search for a book."})

class AuthorSearchSchema(Schema):
    author_name = fields.Str(required=True, error_messages={"required": "Author name is required to search for books by the author."})


class ReservationRequestSchema(Schema):
    author_id = fields.Int(required=True)
    event_id = fields.Int(required=True)