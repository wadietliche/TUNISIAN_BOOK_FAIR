from flask_smorest import abort
from flask import jsonify,request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity,get_jwt
import logging
from datetime import datetime
from webapp import db
from textblob import TextBlob
from webapp.models import Admin, Author, Event, FairMap,Attendee,FavoriteBook,FavoriteAuthor,Book,PresentEvent




def get_user_counts():
    try:
        approved_author_count = Author.query.filter_by(approved=True).count()

        attendee_count = Attendee.query.count()

        return jsonify({
            "total_authors": approved_author_count,
            "total_attendees": attendee_count
        }), 200

    except AttributeError as attr_err:
        return jsonify({
            "error": "Attribute error occurred.",
            "details": str(attr_err)
        }), 500

    except TypeError as type_err:
        return jsonify({
            "error": "Type error occurred.",
            "details": str(type_err)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500



def get_top_books():
    try:
        top_books = (
            db.session.query(Book.title, db.func.count(FavoriteBook.book_id).label('favorites'))
            .join(FavoriteBook, Book.book_id == FavoriteBook.book_id)
            .group_by(Book.title)
            .order_by(db.desc('favorites'))
            .limit(5)
            .all()
        )
        
        if not top_books:
            return jsonify({
                "message": "No books found in the favorites list.",
                "top_books": []
            }), 200

        return jsonify([{"title": book[0], "favorites": book[1]} for book in top_books]), 200

    except AttributeError as attr_err:
        return jsonify({
            "error": "Attribute error occurred.",
            "details": str(attr_err)
        }), 500

    except TypeError as type_err:
        return jsonify({
            "error": "Type error occurred.",
            "details": str(type_err)
        }), 500

    except OperationalError as db_err:
        return jsonify({
            "error": "Database operation error occurred.",
            "details": str(db_err)
        }), 500

    except SQLAlchemyError as sa_err:
        return jsonify({
            "error": "An SQLAlchemy error occurred.",
            "details": str(sa_err)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500
    


def get_event_analytics():
    try:
        total_events = Event.query.count()

        if total_events == 0:
            return jsonify({
                "message": "No events available.",
                "total_events": 0,
                "most_attended_event": None,
                "most_attended_count": 0,
                "average_attendance": 0
            }), 200

        most_attended_event = (
            db.session.query(Event.event_name, db.func.count(PresentEvent.author_id).label('attendance'))
            .select_from(Event)  # Explicitly setting the source of the query
            .join(PresentEvent, Event.event_id == PresentEvent.event_id)
            .group_by(Event.event_name)
            .order_by(db.desc('attendance'))
            .first()
        )

        if not most_attended_event:
            most_attended_event_name = None
            most_attended_event_count = 0
        else:
            most_attended_event_name = most_attended_event[0]
            most_attended_event_count = most_attended_event[1]

        # Calculate attendance per event
        attendance_counts = (
            db.session.query(db.func.count(PresentEvent.author_id))
            .select_from(Event)
            .join(PresentEvent, Event.event_id == PresentEvent.event_id)
            .group_by(Event.event_id)
            .all()
        )

        # Calculate average attendance
        if attendance_counts:
            avg_attendance = sum(count[0] for count in attendance_counts) / len(attendance_counts)
        else:
            avg_attendance = 0

        return jsonify({
            "total_events": total_events,
            "most_attended_event": most_attended_event_name,
            "most_attended_count": most_attended_event_count,
            "average_attendance": avg_attendance
        }), 200

    except AttributeError as attr_err:
        return jsonify({
            "error": "Attribute error occurred.",
            "details": str(attr_err)
        }), 500

    except TypeError as type_err:
        return jsonify({
            "error": "Type error occurred.",
            "details": str(type_err)
        }), 500

    except OperationalError as db_err:
        return jsonify({
            "error": "Database operation error occurred.",
            "details": str(db_err)
        }), 500

    except SQLAlchemyError as sa_err:
        return jsonify({
            "error": "An SQLAlchemy error occurred.",
            "details": str(sa_err)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500





def get_books_by_author():
    try:
        author_books = (
            db.session.query(Author.author_name, db.func.count(Book.book_id).label('book_count'))
            .join(Book, Author.author_id == Book.author_id)
            .group_by(Author.author_name)
            .order_by(db.desc('book_count'))
            .all()
        )

        if not author_books:
            return jsonify({
                "message": "No authors or books found in the database.",
                "authors": []
            }), 200
        return jsonify([
            {"author_name": author[0], "book_count": author[1]} for author in author_books
        ]), 200

    except AttributeError as attr_err:
        return jsonify({
            "error": "Attribute error occurred.",
            "details": str(attr_err)
        }), 500

    except TypeError as type_err:
        return jsonify({
            "error": "Type error occurred.",
            "details": str(type_err)
        }), 500

    except OperationalError as db_err:
        return jsonify({
            "error": "Database operation error occurred.",
            "details": str(db_err)
        }), 500

    except SQLAlchemyError as sa_err:
        return jsonify({
            "error": "An SQLAlchemy error occurred.",
            "details": str(sa_err)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500




def get_feedback_analytics():
    try:
        # Query to fetch feedback and related event names
        feedback_stats = (
            db.session.query(Event.event_name, PresentEvent.feedback)
            .join(PresentEvent, Event.event_id == PresentEvent.event_id)
            .filter(PresentEvent.feedback.isnot(None))
            .all()
        )

        if not feedback_stats:
            return jsonify({
                "message": "No feedback found for any event.",
                "feedback_stats": [],
                "sentiment_summary": {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0
                }
            }), 200

        # Initialize sentiment counters
        positive_count = 0
        neutral_count = 0
        negative_count = 0

        # Process feedback and perform sentiment analysis
        event_feedback = {}
        for event_name, feedback in feedback_stats:
            # Analyze sentiment
            sentiment = TextBlob(feedback).sentiment.polarity
            if sentiment > 0.1:
                positive_count += 1
            elif sentiment < -0.1:
                negative_count += 1
            else:
                neutral_count += 1

            # Group feedback by event
            if event_name not in event_feedback:
                event_feedback[event_name] = []
            event_feedback[event_name].append({
                "feedback": feedback,
                "sentiment_score": sentiment
            })

        # Prepare response
        response = {
            "feedback_stats": [
                {
                    "event_name": event_name,
                    "feedback_count": len(feedbacks),
                    "feedback_details": feedbacks
                }
                for event_name, feedbacks in event_feedback.items()
            ],
            "sentiment_summary": {
                "positive": positive_count,
                "neutral": neutral_count,
                "negative": negative_count
            }
        }

        return jsonify(response), 200

    except AttributeError as attr_err:
        return jsonify({
            "error": "Attribute error occurred.",
            "details": str(attr_err)
        }), 500

    except TypeError as type_err:
        return jsonify({
            "error": "Type error occurred.",
            "details": str(type_err)
        }), 500

    except OperationalError as db_err:
        return jsonify({
            "error": "Database operation error occurred.",
            "details": str(db_err)
        }), 500

    except SQLAlchemyError as sa_err:
        return jsonify({
            "error": "An SQLAlchemy error occurred.",
            "details": str(sa_err)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500
