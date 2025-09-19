import os
import sys
import pytest
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from app import create_app, db
from app.models import User
from app.services import create_user, create_list, create_task

@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
        }
    )
    with app.app_context():
        db.create_all()
        yield app

def test_create_user_and_list(app):
    with app.app_context():
        u = create_user("alice", "password1")
        assert u is not None
        assert u.username == "alice"
        l = create_list(u, "Groceries", "Buy milk")
        assert l.title == "Groceries"
        t = create_task(l, "Buy milk", "2 liters")
        assert t.title == "Buy milk"
