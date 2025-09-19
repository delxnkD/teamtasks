from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
)
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user,
)
from . import db
from .models import User, TaskList, Task, ListShare
from .services import (
    create_user,
    get_user_by_username,
    create_list,
    get_user_lists,
    create_task,
    toggle_task_done,
    delete_task,
    share_list,
    delete_list,
)

# Blueprints
auth_bp = Blueprint("auth", __name__, template_folder="templates")
main_bp = Blueprint("main", __name__, template_folder="templates")
api_bp = Blueprint("api", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user. On success redirect to login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password are required.")
            return render_template("register.html")
        created = create_user(username, password)
        if created:
            flash("Account created. Please log in.")
            return redirect(url_for("auth.login"))
        else:
            flash("Username already exists.")
            return render_template("register.html")
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Simple form login (session-based)."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.index"))
        flash("Invalid credentials.")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@main_bp.route("/")
@login_required
def index():
    """
    Homepage: lists owned and shared lists for the current user.
    Uses service get_user_lists(current_user) which returns {'owned': [...], 'shared': [...]}
    """
    lists = get_user_lists(current_user)
    return render_template("index.html", lists=lists)


@main_bp.route("/lists/new", methods=["GET", "POST"])
@login_required
def lists_new():
    """Create a new TaskList owned by the current user."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title:
            flash("Title is required.")
            return render_template("new_list.html")
        create_list(current_user, title, description)
        return redirect(url_for("main.index"))
    return render_template("new_list.html")


@main_bp.route("/lists/<int:list_id>")
@login_required
def view_list(list_id):
    """
    Render the single list page.

    Permission logic:
      - view: allowed if owner OR shared to current_user (regardless of can_edit)
      - edit/delete: allowed if owner OR shared with can_edit=True
    """
    l = TaskList.query.get_or_404(list_id)

    is_owner = (l.owner_id == current_user.id)
    is_shared_view = any(s.user_id == current_user.id for s in l.shares)
    if not (is_owner or is_shared_view):
        abort(403)

    can_edit = is_owner or any((s.user_id == current_user.id and s.can_edit) for s in l.shares)

    return render_template("list.html", list_obj=l, can_edit=can_edit)


@main_bp.route("/lists/<int:list_id>/share", methods=["POST"])
@login_required
def share_list_view(list_id):
    """
    Share a list with another user (owner only).
    Expects 'username' and an optional 'can_edit' checkbox from the form.
    """
    l = TaskList.query.get_or_404(list_id)
    if l.owner_id != current_user.id:
        abort(403)

    username = request.form.get("username", "").strip()
    can_edit = bool(request.form.get("can_edit"))
    if not username:
        flash("Please specify a username to share with.")
        return redirect(url_for("main.view_list", list_id=list_id))

    target = User.query.filter_by(username=username).first()
    if not target:
        flash("User not found.")
        return redirect(url_for("main.view_list", list_id=list_id))

    share_list(list_id, target.id, can_edit=can_edit)
    flash(f"List shared with {username}.")
    return redirect(url_for("main.view_list", list_id=list_id))



# JSON API endpoints (mounted under /api)
# Note: these endpoints require login and rely on session cookie (same-origin)
@api_bp.route("/lists", methods=["GET"])
@login_required
def api_get_lists():
    """
    Return JSON with owned and shared lists for the current user.
    Format:
      { "owned": [{id,title,description,owner}], "shared": [...] }
    """
    lists = get_user_lists(current_user)

    def _serialize(l: TaskList):
        return {
            "id": l.id,
            "title": l.title,
            "description": l.description,
            "owner": l.owner.username,
        }

    return jsonify({"owned": [_serialize(l) for l in lists["owned"]], "shared": [_serialize(l) for l in lists["shared"]]})


@api_bp.route("/lists/<int:list_id>/tasks", methods=["POST"])
@login_required
def api_create_task(list_id):
    """
    Create a task in the specified list.
    Permission: owner OR shared with can_edit=True.
    Expects JSON body: {"title": "...", "description": "..."}
    """
    task_list = TaskList.query.get_or_404(list_id)

    # permission check: owner or shared with can_edit
    allowed = (task_list.owner_id == current_user.id) or any(
        (s.user_id == current_user.id and s.can_edit) for s in task_list.shares
    )
    if not allowed:
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400

    t = create_task(task_list, title, description)
    return (
        jsonify(
            {"id": t.id, "title": t.title, "description": t.description, "done": t.done}
        ),
        201,
    )


@api_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def api_toggle_task(task_id):
    """
    Toggle a task done state.
    Permission: owner of the list OR shared with can_edit=True.
    Expects JSON body: {"done": true|false} (default true)
    """
    t = Task.query.get_or_404(task_id)
    task_list = t.task_list
    allowed = (task_list.owner_id == current_user.id) or any(
        (s.user_id == current_user.id and s.can_edit) for s in task_list.shares
    )
    if not allowed:
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True) or {}
    done = bool(data.get("done", True))
    t2 = toggle_task_done(task_id, done)
    if not t2:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": t2.id, "done": t2.done})


@api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def api_delete_task(task_id):
    """
    Delete a task.
    Permission: owner of the list OR shared with can_edit=True.
    """
    t = Task.query.get_or_404(task_id)
    task_list = t.task_list
    allowed = (task_list.owner_id == current_user.id) or any(
        (s.user_id == current_user.id and s.can_edit) for s in task_list.shares
    )
    if not allowed:
        return jsonify({"error": "forbidden"}), 403

    success = delete_task(task_id)
    return jsonify({"deleted": bool(success)})
