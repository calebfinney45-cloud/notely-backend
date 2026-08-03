from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.note import Note

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    demo = User(first_name="Demo", last_name="User", email="demo@notely.com",
                password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"))
    db.session.add(demo)
    db.session.commit()

    db.session.add_all([
        Note(title="Welcome", content="This is your first note!", user_id=demo.id),
        Note(title="Groceries", content="Eggs, milk, bread", user_id=demo.id),
    ])
    db.session.commit()
    print("Seeded!")