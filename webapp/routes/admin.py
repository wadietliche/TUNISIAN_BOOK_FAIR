from flask.views import MethodView
from flask import jsonify,request
from flask_smorest import Blueprint
from webapp.models import Admin, Author
from webapp.schemas import AdminSchema,AdminLoginSchema,AuthorApprovalSchema,EventSchema
from webapp.Services import AdminServices
from flask_jwt_extended import jwt_required,get_jwt
from marshmallow import ValidationError



admin_bp = Blueprint("Admins", "admins", description="Operations on Admins")
class CreateAdmin(MethodView):
    
    @jwt_required() 
    @admin_bp.arguments(AdminSchema) 
    def post(self, admin_data):

        try:
            claims = get_jwt()

            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403


            return AdminServices.createNewAdmin(admin_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


admin_bp.add_url_rule('/create', view_func=CreateAdmin.as_view('create_admin'))



# Attendee Login 
@admin_bp.route("/admin/login")
class adminLogin(MethodView):
    @admin_bp.arguments(AdminLoginSchema)
    def post(self,login_data):
        return AdminServices.adminLogin(login_data)



#done
@admin_bp.route("/admin/<int:admin_id>", methods=["GET", "DELETE"])
class AdminResource(MethodView):
    
    @jwt_required()  
    def get(self, admin_id):
        """Retrieve an admin by ID."""
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403


            return AdminServices.getAdminById(admin_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  
    def delete(self, admin_id):
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403


            return AdminServices.delAdminById(admin_id)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


#done
@admin_bp.route("/admin", methods=["GET", "POST"])
class AdminListResource(MethodView):
    
    @jwt_required()  # Ensure the user is authenticated
    def get(self):
        """Retrieve all admins."""
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403

            # Retrieve and return all admins
            return AdminServices.returnAllAdmins()

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @jwt_required()  # Ensure the user is authenticated
    @admin_bp.arguments(AdminSchema)  # Automatically validate incoming JSON data
    @admin_bp.response(201, AdminSchema)  # Serialize and return the Admin object after it's created
    def post(self, admin_data):
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403

            # Create a new admin
            return AdminServices.createNewAdmin(admin_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500



#done
class AdminApproveAuthor(MethodView):
    @jwt_required()  
    def post(self, author_id):
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403
            response = AdminServices.approveAuthor(author_id)
            return jsonify(response[0]), response[1]

        except Exception as e:
            return jsonify({"error": str(e)}), 500

admin_bp.add_url_rule('/admin/approve_author/<int:author_id>', view_func=AdminApproveAuthor.as_view('approve_author'))



#done
@admin_bp.route("/admin/event", methods=["POST", "DELETE"])
class CreateEvent(MethodView):
    @jwt_required() 
    @admin_bp.arguments(EventSchema)  
    def post(self, event_data):
        claims = get_jwt()
        if claims.get("is_admin") != True:
            return jsonify({"message": "Access denied: Administrator privileges are required to access this endpoint."}), 403
        return AdminServices.create_event(event_data)
    
    @jwt_required()
    def delete(self):
        try:

            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({"message": "Access denied: Administrator privileges are required to access this endpoint."}), 403
            

            event_id = request.json.get('event_id')
            if not event_id:
                return jsonify({"message": "Event ID is required."}), 400  
            
            response, status_code = AdminServices.delete_event(event_id)
            return jsonify(response), status_code
        
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    


#done
@admin_bp.route("/admin/author/booth", methods=["PUT"])
class ApproveBoothRequest(MethodView):
    @jwt_required()  
    def put(self):
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403

            data = request.json
            author_id = data.get('author_id')
            booth_reference = data.get('booth_reference')

            if not author_id or not booth_reference:
                return jsonify({
                    "message": "Both author_id and booth_reference are required."
                }), 400

            return AdminServices.approve_and_assign_booth(author_id, booth_reference)
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


#done
@admin_bp.route("/admin/author", methods=["PUT"])
class BanAuthor(MethodView):
    @jwt_required() 
    def put(self):
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403

            return AdminServices.banAuthor()

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
        
#done
@admin_bp.route("/admin/attendee", methods=["DELETE"])
class DeleteAttendee(MethodView):
    @jwt_required() 
    def delete(self):
        try:
            claims = get_jwt()
            if claims.get("is_admin") != True:
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403
            return AdminServices.deleteAttendee()

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    




@admin_bp.route("/adminc", methods=["GET"])
class AdminClaims(MethodView):
    @jwt_required()
    def get(self):
        try:
            claims = AdminServices.returnClaims()
            return jsonify(claims), 200
        except Exception as e:
            
            return jsonify({"error": "An unexpected error occurred"}), 500
        

@admin_bp.route("/admin/attendee", methods=["GET"])
class Managesers(MethodView):
    @jwt_required()
    def get(self):
        try: 
            claims = get_jwt()
            if not claims.get("is_admin"):
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403
            return AdminServices.get_attendee_details()
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
            


@admin_bp.route("/admin/author", methods=["GET"])
class Managesers(MethodView):
    @jwt_required()
    def get(self):
        try: 
            claims = get_jwt()
            if not claims.get("is_admin"):
                return jsonify({
                    "message": "Access denied: Administrator privileges are required to access this endpoint."
                }), 403
            return AdminServices.get_all_authors()
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
