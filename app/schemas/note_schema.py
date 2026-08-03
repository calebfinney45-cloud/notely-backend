from app.extensions import ma
from app.models.note import Note

class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note
        load_instance = True

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)