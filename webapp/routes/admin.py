from flask.views import MethodView
from flask import jsonify,request
from flask_smorest import Blueprint
from webapp.models import Admin, Author
from webapp.schemas import AdminSchema,AdminLoginSchema,AuthorApprovalSchema,EventSchema
from webapp.Services import AdminServices
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError


# Create the Blueprint for Admin
admin_bp = Blueprint("Admins", "admins", description="Operations on Admins")


@admin_bp.route("/create")
class CreateAdmin(MethodView):
    @admin_bp.arguments(AdminSchema)
    def post(self, admin_data):
        """
        Endpoint to create a new admin.
        """
        return AdminServices.createNewAdmin(admin_data)



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
#@jwt_required()
class AdminListResource(MethodView):
    def get(self):
        """Retrieve all admins."""
        return AdminServices.returnAllAdmins()
    

    
    @admin_bp.arguments(AdminSchema)  # Automatically validate incoming JSON data
    @admin_bp.response(201, AdminSchema)  # Serialize and return the Admin object after it's created
    


    def post(self, admin_data):
        return AdminServices.createNewAdmin(admin_data)




class AdminApproveAuthor(MethodView):
    @jwt_required()
    def post(self, author_id):
        # Call the service method that handles approving the author
        response = AdminServices.approveAuthor(author_id)
        
        # Return the response as JSON with the appropriate HTTP status code
        return jsonify(response[0]), response[1]

# Register the AdminApproveAuthor method view with the blueprint
admin_bp.add_url_rule('/admin/approve_author/<int:author_id>', view_func=AdminApproveAuthor.as_view('approve_author'))




@admin_bp.route("/admin/event", methods=["POST", "DELETE"])
#@jwt_required()
class CreateEvent(MethodView):
    @admin_bp.arguments(EventSchema)  # Automatically validate incoming JSON data
    def post(self, event_data):
        return AdminServices.create_event(event_data)
    



@admin_bp.route("/admin/author/booth", methods=["PUT"])
class ApproveBoothRequest(MethodView):
    def put(self):
        try:
            # Extract the request data
            data = request.json
            author_id = data.get('author_id')
            booth_reference = data.get('booth_reference')

            if not author_id or not booth_reference:
                return jsonify({
                    "message": "Both author_id and booth_reference are required."
                }), 400

            # Call the service function
            return AdminServices.approve_and_assign_booth(author_id, booth_reference)
        except Exception as e:
            return jsonify({"error": str(e)}), 500