from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user, remember=True)
            return redirect(url_for("routes.home"))
        else:
            flash("There is no account with these credentials", category="error")

    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.index"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords dont match", category="error")
            return redirect(url_for("auth.sign_up"))
        
        new_user = User(username=username, password=password1)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully", category="success")
        login_user(new_user)
        return redirect(url_for("routes.home"))

    return render_template("sign_up.html", user=current_user)
