from flask import Blueprint, request, jsonify, abort
from flask.views import MethodView
from webapp import db
from webapp.models import Author, Book, FairMap, PresentEvent, Event
from webapp.schemas import AuthorSchema, BookSchema, ReservationRequestSchema
from sqlalchemy.exc import SQLAlchemyError
from webapp.Services import AuthorSercices




author_bp = Blueprint("authors", __name__, description="Operations related to Authors")



@author_bp.route("/author/signup", methods=["POST"])
class AuthorSignup(MethodView):
    def post(self):
        return AuthorSercices.authorSignUp



# Route for author login
@author_bp.route("/author/login", methods=["POST"])
class AuthorLogin(MethodView):
    def post(self):
        return AuthorSercices.authorLogin()



# Route to add a new book
@author_bp.route("/author/book", methods=["POST"])
class AddBook(MethodView):
    @author_bp.arguments(BookSchema)
    def post(self, book_data):
        return AuthorSercices.addBookByAuthor(book_data)



# Route to send a reservation request for an event
@author_bp.route("/author/reservation", methods=["POST"])
class ReservationRequest(MethodView):
    def post(self):
        return AuthorSercices.reservationRequest()