from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models.user import User
from app.schemas.user_schema import user_schema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    username = data.get("username") or data.get("first_name") or "User"
    name_parts = username.split(maxsplit=1)
    first_name = name_parts[0] if name_parts else "User"
    last_name = name_parts[1] if len(name_parts) > 1 else "User"

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=data["email"],
        password_hash=hashed
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "token": token, "user": user_schema.dump(user)}), 201

@auth_bp.route("/register", methods=["POST"])
def register():
    return signup()

@auth_bp.route("/auth/login", methods=["POST"])
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(email=data.get("email")).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "token": token, "user": user_schema.dump(user)}), 200

@auth_bp.route("/auth/me", methods=["GET"])
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user_schema.dump(user)}), 200