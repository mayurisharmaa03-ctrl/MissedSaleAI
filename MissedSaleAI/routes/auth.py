"""
Authentication routes for MissedSale AI.
Supports password verification, demo quick-login, and session management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template("login.html")

@auth_bp.route("/quick-demo-login")
def quick_demo_login():
    """Allows one-click demo login during presentations."""
    user = User.query.filter_by(username="admin").first()
    if not user:
        user = User(username="admin", email="admin@missedsale.ai", role="admin")
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role
    flash("Logged in with Demo Admin credentials.", "info")
    return redirect(url_for("dashboard.index"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
