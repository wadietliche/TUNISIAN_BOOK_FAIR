from webapp import db



# Admin Table
class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)


# Attendees Table
class Attendee(db.Model):
    __tablename__ = 'attendees'
    attendee_id = db.Column(db.Integer, primary_key=True)
    attendee_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    favorite_books = db.relationship('FavoriteBook', backref='attendee', lazy=True)
    favorite_authors = db.relationship('FavoriteAuthor', back_populates='attendee', lazy=True)  # Use back_populates here


# Authors Table
# Authors Table
class Author(db.Model):
    __tablename__ = 'authors'
    
    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    approved = db.Column(db.Boolean, default=False)  

    # backref 'books' in Author model remains
    books = db.relationship('Book', backref='author_relation', lazy=True)  # Changed 'author' to 'author_relation'
    fair_maps = db.relationship('FairMap', backref='author', lazy=True)
    present_events = db.relationship('PresentEvent', backref='author', lazy=True)
    favorite_authors = db.relationship('FavoriteAuthor', back_populates='author')




# Books Table
class Book(db.Model):
    __tablename__ = 'books'
    
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(50), unique=True, nullable=False)
    published_year = db.Column(db.Integer)
    publisher = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), nullable=False)
    
    author = db.relationship('Author', backref=db.backref('author_books', lazy=True))  # Changed to 'author_books'







# Events Table
class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    start_hour = db.Column(db.Time, nullable=False)
    final_hour = db.Column(db.Time, nullable=False)
    present_events = db.relationship('PresentEvent', backref='event', lazy=True)


# FavoriteBooks Table 
class FavoriteBook(db.Model):
    __tablename__ = 'favorite_books'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True)
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.attendee_id'), primary_key=True)




# FairMap Table 
class FairMap(db.Model):
    __tablename__ = 'fair_map'
    booth_reference = db.Column(db.String(50), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved'


# PresentEvent Table 
class PresentEvent(db.Model):
    __tablename__ = 'present_event'
    
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), primary_key=True)
    feedback = db.Column(db.String(500), nullable=True)  




class FavoriteAuthor(db.Model):
    __tablename__ = 'favorite_authors'
    favorite_author_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), nullable=False)
    attendee_id = db.Column(db.Integer, db.ForeignKey('attendees.attendee_id'), nullable=False)

    attendee = db.relationship('Attendee', back_populates='favorite_authors')
    author = db.relationship('Author', back_populates='favorite_authors') 