from flask import request, jsonify
from flask_smorest import Blueprint, abort
from flask.views import MethodView

from db import users
import uuid
# Create the blueprint
user_bp = Blueprint("user", __name__)

@user_bp.route("/user")
class Usering(MethodView):
    def post(self):
        user_data= request.get_json()
        if (
            "full name" not in user_data
            or "email" not in user_data
            or "password" not in user_data
        ):
            abort(405,status="Bad request, Ensure 'fullname', 'email', 'password' are included in the JSON payload")
        for jj in users.values():
            if (
                user_data["email"]==jj["email"]
                ):
                    abort(400, status="user already exists.")
        user_id = uuid.uuid4().hex
        user = {**user_data,"id":user_id}
        users[user_id]=user
        return jsonify(user), 200
    
@user_bp.route("/user/<user_id>")
class UserMngmnt(MethodView):
    def get(self,user_id):
         try:
              return users[user_id]
         except KeyError:
              abort(404, message="user doesn't exist")
    
    def put(self,user_id):
        user_data=request.get_json()
        if (
            "full name" not in user_data
            or "email" not in user_data
            or "password" not in user_data
        ):
            abort(405,status="Bad request, Ensure 'fullname', 'email', 'password' are included in the JSON payload")
        try:
            user = users[user_id]
            user |= user_data
            return user
        except KeyError:
            abort(404, message="user not found.")

    def delete(self, user_id):
         try:
              del users[user_id]
              return{"message":"user deleted."}
         except KeyError:
              abort(404, message="User not found.")