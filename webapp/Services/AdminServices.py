from webapp.models import Admin, Author
from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db



def getAdminById(admin_id):
    admin = Admin.query.get_or_404(admin_id)
    return {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name
    }



def delAdminById(admin_id):
    """Delete an admin by ID."""
    admin = Admin.query.get_or_404(admin_id)
    db.session.delete(admin)
    db.session.commit()
    return {"message": "Admin deleted"}, 200



def createNewAdmin(admin_data):
    """Create a new admin."""
    try:
        # Create Admin from validated admin_data
        admin = Admin(**admin_data)
        db.session.add(admin)  # Add the new Admin to the session
        db.session.commit()  # Commit the transaction
        return admin  # Return the created Admin
    except IntegrityError:
        # Handle integrity errors (e.g., duplicate admin name)
        db.session.rollback()  # Rollback the session to avoid partial commits
        abort(400, message="An admin with this name already exists.")
    except SQLAlchemyError as e:
        # Handle other SQLAlchemy errors (e.g., database connection issues)
        db.session.rollback()  
        abort(500, message=f"An error occurred while processing your request: {str(e)}")



def returnAllAdmins():
    admins = Admin.query.all()
    return [
            {"admin_id": admin.admin_id, "admin_name": admin.admin_name}
            for admin in admins
        ]



def approveAuthor(author_id):
    author = Author.query.get_or_404(author_id)
    # Approve the author
    author.approved = True
    db.session.commit()
    return {"message": f"Author {author.author_name} has been approved."}, 200