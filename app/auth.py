from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print(request.form.get("username"))
        print(request.form.get("password"))

    return render_template("login.html")

@auth.route("/logout")
def logout():
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

        flash("Account created", category="success")
        return redirect(url_for("routes.home"))

    return render_template("sign_up.html")
