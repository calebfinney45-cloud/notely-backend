from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.note import Note
from app.schemas.note_schema import note_schema, notes_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")
documents_bp = Blueprint("documents", __name__, url_prefix="/documents")


def _get_user_id():
    return int(get_jwt_identity())


def _serialize_note(note):
    payload = note_schema.dump(note)
    return {"document": payload, "note": payload}


@notes_bp.route("", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = _get_user_id()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    pagination = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        "notes": notes_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages
    }), 200

@notes_bp.route("", methods=["POST"])
@jwt_required()
def create_note():
    data = request.get_json(silent=True) or {}
    note = Note(
        title=data.get("title", "Untitled"),
        content=data.get("content", ""),
        user_id=_get_user_id(),
        parent_id=data.get("parent_id"),
        is_archived=data.get("is_archived", False),
        is_published=data.get("is_published", False),
        cover_image=data.get("cover_image"),
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(_serialize_note(note)), 201

@notes_bp.route("/<int:note_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
@jwt_required()
def note_detail(note_id):
    note = Note.query.filter_by(id=note_id, user_id=_get_user_id()).first_or_404()

    if request.method == "DELETE":
        db.session.delete(note)
        db.session.commit()
        return "", 204

    data = request.get_json(silent=True) or {}
    if request.method in {"PUT", "PATCH"}:
        note.title = data.get("title", note.title)
        note.content = data.get("content", note.content)
        note.parent_id = data.get("parent_id", note.parent_id)
        note.is_archived = data.get("is_archived", note.is_archived)
        note.is_published = data.get("is_published", note.is_published)
        note.cover_image = data.get("cover_image", note.cover_image)
        db.session.commit()

    return jsonify(_serialize_note(note)), 200


@documents_bp.route("", methods=["GET"])
@jwt_required()
def get_documents():
    user_id = _get_user_id()
    documents = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).all()
    return jsonify({"documents": notes_schema.dump(documents)}), 200

@documents_bp.route("", methods=["POST"])
@jwt_required()
def create_document():
    data = request.get_json(silent=True) or {}
    note = Note(
        title=data.get("title", "Untitled"),
        content=data.get("content", ""),
        user_id=_get_user_id(),
        parent_id=data.get("parent_id"),
        is_archived=data.get("is_archived", False),
        is_published=data.get("is_published", False),
        cover_image=data.get("cover_image"),
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({"document": note_schema.dump(note)}), 201

@documents_bp.route("/sidebar", methods=["GET"])
@jwt_required()
def get_sidebar_documents():
    user_id = _get_user_id()
    parent_id = request.args.get("parent_id", type=int)
    query = Note.query.filter_by(user_id=user_id)
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    else:
        query = query.filter_by(parent_id=None)
    documents = query.order_by(Note.updated_at.desc()).all()
    return jsonify({"sidebar": notes_schema.dump(documents)}), 200

@documents_bp.route("/search", methods=["GET"])
@jwt_required()
def search_documents():
    user_id = _get_user_id()
    q = (request.args.get("q") or "").strip()
    if not q:
        documents = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).all()
    else:
        documents = Note.query.filter(Note.user_id == user_id).filter(
            (Note.title.ilike(f"%{q}%")) | (Note.content.ilike(f"%{q}%"))
        ).order_by(Note.updated_at.desc()).all()
    return jsonify({"documents": notes_schema.dump(documents)}), 200

@documents_bp.route("/<int:note_id>", methods=["GET", "PATCH", "PUT", "DELETE"])
@jwt_required()
def document_detail(note_id):
    note = Note.query.filter_by(id=note_id, user_id=_get_user_id()).first_or_404()

    if request.method == "DELETE":
        db.session.delete(note)
        db.session.commit()
        return "", 204

    data = request.get_json(silent=True) or {}
    if request.method in {"PUT", "PATCH"}:
        note.title = data.get("title", note.title)
        note.content = data.get("content", note.content)
        note.parent_id = data.get("parent_id", note.parent_id)
        note.is_archived = data.get("is_archived", note.is_archived)
        note.is_published = data.get("is_published", note.is_published)
        note.cover_image = data.get("cover_image", note.cover_image)
        db.session.commit()

    return jsonify({"document": note_schema.dump(note)}), 200