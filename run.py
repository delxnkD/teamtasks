import sys
from app import create_app, db
from app.models import User
from getpass import getpass

app = create_app()

def init_db(create_admin=True):
    with app.app_context():
        db.create_all()
        if create_admin:
            if not User.query.filter_by(username="admin").first():
                print("Creating default admin account (username: admin)")
                pwd = "adminpass"
                u = User(username="admin", role="admin")
                u.set_password(pwd)
                db.session.add(u)
                db.session.commit()
                print("Admin created with password:", pwd)
            else:
                print("Admin user already exists.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init-db":
        init_db()
        print("DB initialized.")
        sys.exit(0)
    app.run(debug=True)
