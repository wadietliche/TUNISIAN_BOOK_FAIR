from flask.views import MethodView
from flask_smorest import Blueprint
from webapp.models import Admin, Author
from webapp.schemas import AdminSchema,AdminLoginSchema
from webapp.Services import AdminServices
from flask_jwt_extended import jwt_required


# Create the Blueprint for Admin
admin_bp = Blueprint("Admins", "admins", description="Operations on Admins")





# Attendee Login (POST request to authenticate)
@admin_bp.route("/admin/login")
class adminLogin(MethodView):
    @admin_bp.arguments(AdminLoginSchema)
    def post(self,login_data):
        return AdminServices.adminLogin(login_data)




# Admin resource for handling a specific admin by ID (GET and DELETE)
@admin_bp.route("/admin/<int:admin_id>", methods=["GET", "DELETE"])
@jwt_required()
class AdminResource(MethodView):
    def get(self, admin_id):
        """Retrieve an admin by ID."""
        return AdminServices.getAdminById(admin_id)



    def delete(self, admin_id):
        return AdminServices.delAdminById(admin_id)



# Admin resource for handling a list of admins (GET all) and creating new admin (POST)
@admin_bp.route("/admin", methods=["GET", "POST"])
@jwt_required()
class AdminListResource(MethodView):
    def get(self):
        """Retrieve all admins."""
        return AdminServices.returnAllAdmins()
    

    
    @admin_bp.arguments(AdminSchema)  # Automatically validate incoming JSON data
    @admin_bp.response(201, AdminSchema)  # Serialize and return the Admin object after it's created
    


    def post(self, admin_data):
        return AdminServices.createNewAdmin(admin_data)



@admin_bp.route("/admin/approve_author/<int:author_id>", methods=["POST"])
@jwt_required()
class AdminApproveAuthor(MethodView):
    def post(self, author_id):
        return AdminServices.approveAuthor()