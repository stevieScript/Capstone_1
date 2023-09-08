from flask import Blueprint, render_template, redirect, flash, session, g, request
from sqlalchemy.exc import IntegrityError
from models import db, User, Playlist
from forms import SignUpForm, LoginForm, EditUserForm
from helper_functions import get_token, get_pop_recommendations

CURR_USER_KEY = "curr_user"

user_bp = Blueprint('user', __name__, template_folder='templates', static_folder='static')

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@user_bp.route("/register", methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already taken", "danger")
            elif User.query.filter_by(email=form.email.data).first():
                flash("Email already taken", "danger")
            return render_template("register.html", form=form)

        do_login(user)
        flash(f"Welcome, maestro {user.username}!", "success")
        return redirect(f"/user")
    else:
        return render_template("register.html", form=form)

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    form = LoginForm()
    try:
        if form.validate_on_submit():
            user = User.authenticate(form.username.data, form.password.data)
            if user:
                do_login(user)
                return redirect(f"/user")
            flash("Invalid credentials.", "danger")
        return render_template("/user/login.html", form=form), 200
    except:
        flash("Something went wrong. Please try again.", "danger")
        return redirect("/")

@user_bp.route("/logout")
def logout():
    """Handle logout of user."""
    do_logout()
    flash("Logged out", "success")
    return redirect("/")

@user_bp.route("/")
def user_profile():
    """Show user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try:
        user = g.user
        playlists = Playlist.query.filter(Playlist.user_id == user.id).all()
        token = get_token()
        result = get_pop_recommendations(token)
        return render_template(
            "/user/user.html", user=user, playlists=playlists, result=result), 200
    except:
        flash("Something went wrong. Please try again.", "danger")
        return redirect("/")

@user_bp.route("/delete", methods=["POST"])
def delete_user():
    """Delete user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try:
        user = g.user
        db.session.delete(user)
        db.session.commit()
        do_logout()
        flash("User deleted", "success")
        return redirect("/")
    except:
        flash("Something went wrong. Please try again.", "danger")
        return redirect("/")

@user_bp.route("/edit", methods=["GET", "POST"])
def edit_user():
    """Edit user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    try:
        user = g.user
        form = EditUserForm(obj=user)

        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash("User updated", "success")
            return redirect(f"/user"), 200
        else:
            return render_template("/user/edit_user.html", form=form, user=user), 200
    except:
        flash("Something went wrong. Please try again.", "danger")
        return redirect("/")