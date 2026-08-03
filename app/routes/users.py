from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from app.schemas.user_schema import user_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_profile():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.profile_picture = data.get("profile_picture", user.profile_picture)
    db.session.commit()
    return jsonify(user_schema.dump(user)), 200

@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_account():
    user = User.query.get(get_jwt_identity())
    db.session.delete(user)
    db.session.commit()
    return "", 204