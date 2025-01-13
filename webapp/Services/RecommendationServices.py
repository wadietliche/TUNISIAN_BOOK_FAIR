from webapp.models import db, Book, FavoriteBook
import requests
import logging
from typing import List, Dict, Optional
from functools import lru_cache
from difflib import SequenceMatcher
from flask import jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
API_KEY = 'AIzaSyCcdNKnm3UL-UK2ykcMoHMvwCmoyhHCkoo'
BASE_URL = 'https://www.googleapis.com/books/v1/volumes'

def _title_similarity(title1: str, title2: str) -> float:
    """Calculate similarity ratio between two titles."""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio()

@lru_cache(maxsize=100)
def _get_similar_books(title: str, author: str, max_results: int = 4) -> List[Dict]:
    """Get similar books using Google Books API with caching."""
    logger.info(f"Searching for books similar to '{title}' by '{author}'")

    try:
        search_queries = [
            f'inauthor:"{author}"',
            f'intitle:"{title}"',
            f'{title} {author}'
        ]

        all_books = []
        for query in search_queries:
            params = {
                'q': query,
                'maxResults': 10,
                'key': API_KEY,
                'orderBy': 'relevance'
            }

            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data:
                continue

            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                if not volume_info.get('title'):
                    continue

                # Avoid duplicates
                if any(
                    _title_similarity(book['title'], volume_info['title']) > 0.8
                    for book in all_books
                ):
                    continue

                book = {
                    'id': item.get('id', ''),
                    'title': volume_info.get('title', ''),
                    'author': volume_info.get('authors', ['Unknown'])[0],
                    'publisher': volume_info.get('publisher', 'Unknown'),
                    'published_year': volume_info.get('publishedDate', '').split('-')[0],
                    'description': volume_info.get('description', '')[:500],
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                    'info_link': volume_info.get('infoLink', '')
                }
                all_books.append(book)

        all_books.sort(key=lambda x: x['author'].lower() == author.lower(), reverse=True)
        return all_books[:max_results]

    except requests.RequestException as e:
        logger.error(f"Google Books API request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Error in _get_similar_books: {e}", exc_info=True)
        return []

def _get_favorite_book(attendee_id: int) -> Optional[Dict]:
    """Get the attendee's most recent favorite book."""
    try:
        favorite = (
            db.session.query(FavoriteBook)
            .filter(FavoriteBook.attendee_id == attendee_id)
            .order_by(FavoriteBook.book_id.desc())  # Order by book_id or other relevant field
            .first()
        )
        
        if not favorite:
            return None
            
        book = db.session.query(Book).get(favorite.book_id)
        if not book:
            return None
            
        # Get author name safely
        author_name = book.author_relation.author_name if book.author_relation else "Unknown"
        
        book_data = {
            'id': book.book_id,
            'title': book.title,
            'author': author_name,
            'description': book.description if hasattr(book, 'description') else ''
        }
        
        logger.info(f"Found favorite book: {book_data['title']}")
        return book_data
        
    except Exception as e:
        logger.error(f"Error fetching favorite book: {str(e)}", exc_info=True)
        return None


def recommend_books_for_attendee(attendee_data: dict) -> Dict:
    """Recommend books based on the attendee's favorite book."""
    logger.info(f"Processing recommendation for attendee: {attendee_data}")

    try:
        attendee_id = attendee_data.get('attendee_id')
        if not attendee_id:
            return {'status': 'error', 'message': 'No attendee_id provided', 'recommendations': []}

        favorite_book = _get_favorite_book(attendee_id)
        if not favorite_book:
            return {
                'status': 'error',
                'message': f'No favorite book found for attendee {attendee_id}',
                'recommendations': []
            }

        similar_books = _get_similar_books(
            title=favorite_book['title'],
            author=favorite_book['author'],
            max_results=7
        )

        return jsonify({
        "favorite_book": favorite_book,
        "similar_books": similar_books
        }), 200

    except Exception as e:
        logger.error(f"Error in recommend_books_for_attendee: {e}", exc_info=True)
        return {'status': 'error', 'message': str(e), 'recommendations': []}