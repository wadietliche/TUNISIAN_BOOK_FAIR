from webapp import create_app, db
from webapp.models import *

app = create_app()

# Create tables in the database
with app.app_context():
    db.create_all()

if __name__=='__main__': #only if we run this it runs the web serve not when imported
    # Create tables in the database
    with app.app_context():
        db.create_all()
    app.run(debug=True)