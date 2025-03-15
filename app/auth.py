from flask import Blueprint, render_template, request, redirect, url_for

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print(request.form.get("username"))
        print(request.form.get("password"))

    return render_template("login.html")

@auth.route("/logout")
def logout():
    return redirect(url_for("routes.home"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    return render_template("sign_up.html")
