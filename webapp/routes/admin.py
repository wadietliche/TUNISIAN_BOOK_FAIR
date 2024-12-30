from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webapp import db
from webapp.models import Admin, Author
from webapp.schemas import AdminSchema

# Create the Blueprint for Admin
admin_bp = Blueprint("Admins", "admins", description="Operations on Admins")

# Admin resource for handling a specific admin by ID (GET and DELETE)
@admin_bp.route("/admin/<int:admin_id>", methods=["GET", "DELETE"])
class AdminResource(MethodView):
    def get(self, admin_id):
        """Retrieve an admin by ID."""
        admin = Admin.query.get_or_404(admin_id)
        return {
            "admin_id": admin.admin_id,
            "admin_name": admin.admin_name
        }

    def delete(self, admin_id):
        """Delete an admin by ID."""
        admin = Admin.query.get_or_404(admin_id)
        db.session.delete(admin)
        db.session.commit()
        return {"message": "Admin deleted"}, 200


# Admin resource for handling a list of admins (GET all) and creating new admin (POST)
@admin_bp.route("/admin", methods=["GET", "POST"])
class AdminListResource(MethodView):
    def get(self):
        """Retrieve all admins."""
        admins = Admin.query.all()
        return [
            {"admin_id": admin.admin_id, "admin_name": admin.admin_name}
            for admin in admins
        ]
    
    @admin_bp.arguments(AdminSchema)  # Automatically validate incoming JSON data
    @admin_bp.response(201, AdminSchema)  # Serialize and return the Admin object after it's created
    def post(self, admin_data):
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

@admin_bp.route("/admin/approve_author/<int:author_id>", methods=["POST"])
class AdminApproveAuthor(MethodView):
    def post(self, author_id):
        author = Author.query.get_or_404(author_id)
        
        # Approve the author
        author.approved = True
        db.session.commit()

        return {"message": f"Author {author.author_name} has been approved."}, 200
