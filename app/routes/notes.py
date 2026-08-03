from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.note import Note
from app.schemas.note_schema import note_schema, notes_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")

@notes_bp.route("", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    pagination = Note.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
    return jsonify({
        "notes": notes_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages
    }), 200

@notes_bp.route("", methods=["POST"])
@jwt_required()
def create_note():
    data = request.get_json()
    note = Note(title=data["title"], content=data["content"], user_id=get_jwt_identity())
    db.session.add(note)
    db.session.commit()
    return jsonify(note_schema.dump(note)), 201

@notes_bp.route("/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=get_jwt_identity()).first_or_404()
    data = request.get_json()
    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()
    return jsonify(note_schema.dump(note)), 200

@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=get_jwt_identity()).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return "", 204