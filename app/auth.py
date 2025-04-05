from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, login_user, logout_user, current_user
from password_strength import PasswordPolicy
from flask_mail import Message
from .models import User
from . import db, hashing, mail
from functools import wraps
from threading import Thread

auth = Blueprint('auth', __name__)
password_policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.session.execute(db.select(User).filter_by(username=username)).scalar()
        if user and hashing.check_value(user.password, password, username):
            login_user(user)
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
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords dont match", category="error")
            return redirect(url_for("auth.sign_up"))
        
        if len(password_policy.test(password1)) != 0:
            flash("Must be at least 8 characters, include a number, uppercase letter, and a special character.", category="error")
            return redirect(url_for("auth.sign_up"))

        user = db.session.execute(db.select(User).filter_by(username=username)).scalar()
        if user:
            flash("Username already in use", category="error")
            return redirect(url_for("auth.sign_up"))

        # use as salt the username, unique each time, not ideal but good for now
        # TODO: make salt a random number and store it in plain text ?
        password = hashing.hash_value(password1, username)

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully, a verification link has been sent to your email", category="success")
        login_user(new_user)

        token = hashing.hash_value(password)
        msg = Message(
            subject="Recipity mail verification",
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[new_user.email],
        )

        # http://localhost:5000/auth/confirm/{new_user.id}?token={token}
        msg.body = f'''
            Welcome to Recipity! Click the link below to confirm your email address
            { url_for('auth.confirm_mail', user_id=new_user.id, token=token, _external=True) }
        '''
        Thread(target=send_mail, args=(current_app._get_current_object(), msg)).start()

        return redirect(url_for("routes.home"))

    return render_template("sign_up.html", user=current_user)

def send_mail(app, msg):
    print("Sending mail")
    with app.app_context():
        mail.send(msg)
    print("Sent mail")

@auth.route("/confirm/<int:user_id>")
def confirm_mail(user_id):
    if "token" not in request.args.keys():
        return "No token provided"

    user = db.get_or_404(User, user_id)

    if user.is_verified:
        return "User already verified"

    token_provided = request.args["token"]

    if not hashing.check_value(token_provided, user.password):
        return "Invalid token"

    user.is_verified = True
    db.session.commit()
    return render_template("verified.html")


def verified_required(func):
    @wraps(func)
    def wrapper_func(*args,**kwargs):
        if not current_user.is_verified:
            return render_template("unverified.html", user=current_user)
    
        return func(*args,**kwargs)

    return wrapper_func