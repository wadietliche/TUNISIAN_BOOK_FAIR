from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from webapp.models import Attendee, FavoriteBook, FavoriteAuthor, Event, PresentEvent, FairMap, db,Author, Book
from webapp.Services import RecommendationServices
from typing import List, Dict, Optional
from datetime import datetime



template = """
You are a helpful assistant for the Tunisian Book Fair. Your goal is to make the book fair experience more user-friendly.
Use the following conversation history, user preferences, and event details to provide personalized and accurate responses.
make sure not to make up anything your data must be relevant to what is provided by the functions.
be super interactive and friendly.

Conversation History: {context}

User Preferences:
- Favorite Books: {favorite_books}
- Favorite Authors: {favorite_authors}

Event Details:
- Upcoming Events: {upcoming_events}
- Booth Locations: {booth_locations}

Question: {question}

Answer:
"""



model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model



def get_favorite_books_and_authors(attendee_id: int) -> Dict[str, List[str]]:
    """
    Fetch the attendee's favorite books and authors from the database.
    :param attendee_id: The ID of the attendee.
    :return: A dictionary containing favorite books and authors.
    """
    try:
        favorite_books = (
            db.session.query(Book.title)
            .join(FavoriteBook, FavoriteBook.book_id == Book.book_id)
            .filter(FavoriteBook.attendee_id == attendee_id)
            .all()
        )
        favorite_authors = (
            db.session.query(Author.author_name)
            .join(FavoriteAuthor, FavoriteAuthor.author_id == Author.author_id)
            .filter(FavoriteAuthor.attendee_id == attendee_id)
            .all()
        )
        return {
            "favorite_books": [book.title for book in favorite_books],
            "favorite_authors": [author.author_name for author in favorite_authors],
        }
    except Exception as e:
        raise Exception(f"Error fetching favorite books and authors: {str(e)}")

def get_upcoming_events() -> List[Dict]:
    """
    Fetch upcoming events from the database.
    :return: A list of upcoming events.
    """
    try:
        events = Event.query.all()  # Get all events from the database
        events_list = []

        # Loop through each event and append the event details in dictionary format
        for event in events:
            events_list.append({
                "event_name": event.event_name,
                "location": event.location,
                "duration": event.duration,
                "start_hour": event.start_hour.strftime('%H:%M:%S'),  # Formatting the time
                "final_hour": event.final_hour.strftime('%H:%M:%S')  # Formatting the time
            })

        return events_list, 200  # Return the list of events with a 200 status

    except Exception as e:
        raise Exception(f"Error fetching upcoming events: {str(e)}")  # Handle any potential errors



def get_booth_locations(author_names: List[str]) -> List[Dict]:
    """
    Fetch booth locations for the given authors.
    :param author_names: A list of author names.
    :return: A list of booth locations.
    """
    try:
        booths = (
            db.session.query(FairMap.booth_reference, Author.author_name)
            .join(Author, FairMap.author_id == Author.author_id)
            .filter(Author.author_name.in_(author_names))
            .all()
        )
        return [
            {"author_name": booth.author_name, "booth_reference": booth.booth_reference}
            for booth in booths
        ]
    except Exception as e:
        raise Exception(f"Error fetching booth locations: {str(e)}")

def generate_chatbot_response(user_input: str, context: str, attendee_id: int) -> str:
    """
    Generates a response using the LLaMA model via Ollama and LangChain.
    :param user_input: The user's input message.
    :param context: The conversation history.
    :param attendee_id: The ID of the attendee (for personalized responses).
    :return: The chatbot's response.
    """
    try:
        preferences = get_favorite_books_and_authors(attendee_id)
        favorite_books = preferences.get("favorite_books", [])
        favorite_authors = preferences.get("favorite_authors", [])

        # Fetch the upcoming events and unpack the tuple
        upcoming_events, _ = get_upcoming_events()  # Unpack the tuple to get only the event list
        booth_locations = get_booth_locations(favorite_authors)

        # Prepare the input data for the chatbot model
        input_data = {
            "context": context,
            "favorite_books": ", ".join(favorite_books) if favorite_books else "None",
            "favorite_authors": ", ".join(favorite_authors) if favorite_authors else "None",
            "upcoming_events": "\n".join([f"{event['event_name']} at {event['location']} ({event['start_hour']} - {event['final_hour']})" for event in upcoming_events]),
            "booth_locations": "\n".join([f"{booth['author_name']} is at {booth['booth_reference']}" for booth in booth_locations]),
            "question": user_input,
        }

        # Generate the chatbot response using LangChain
        result = chain.invoke(input_data)
        return result
    except Exception as e:
        raise Exception(f"Error generating chatbot response: {str(e)}")
