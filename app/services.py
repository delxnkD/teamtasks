
from . import db
from .models import User, TaskList, Task, ListShare
from sqlalchemy.exc import IntegrityError

# User service
def create_user(username, password, role="user"):
    u = User(username=username, role=role)
    u.set_password(password)
    db.session.add(u)
    try:
        db.session.commit()
        return u
    except IntegrityError:
        db.session.rollback()
        return None

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

# List & task services
def create_list(owner: User, title: str, description: str = ""):
    tl = TaskList(title=title, description=description, owner=owner)
    db.session.add(tl)
    db.session.commit()
    return tl

def get_user_lists(user: User):
    owned = TaskList.query.filter_by(owner_id=user.id).all()
    shared_list_ids = [s.list_id for s in user_shares(user)]
    shared = TaskList.query.filter(TaskList.id.in_(shared_list_ids)).all() if shared_list_ids else []
    return {"owned": owned, "shared": shared}

def user_shares(user: User):
    return ListShare.query.filter_by(user_id=user.id).all()

def share_list(list_id: int, user_id: int, can_edit: bool = False):
    existing = ListShare.query.filter_by(list_id=list_id, user_id=user_id).first()
    if existing:
        existing.can_edit = can_edit
        db.session.commit()
        return existing
    share = ListShare(list_id=list_id, user_id=user_id, can_edit=can_edit)
    db.session.add(share)
    db.session.commit()
    return share

def create_task(list_: TaskList, title: str, description: str = ""):
    t = Task(title=title, description=description, task_list=list_)
    db.session.add(t)
    db.session.commit()
    return t

def toggle_task_done(task_id: int, done: bool):
    t = Task.query.get(task_id)
    if not t:
        return None
    t.done = done
    db.session.commit()
    return t

def delete_task(task_id: int):
    t = Task.query.get(task_id)
    if not t:
        return False
    db.session.delete(t)
    db.session.commit()
    return True

def delete_list(list_id: int):
    l = TaskList.query.get(list_id)
    if not l:
        return False
    db.session.delete(l)
    db.session.commit()
    return True
