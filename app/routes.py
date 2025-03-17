from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from .models import Recipe, User
from . import db, UPLOAD_FOLDER, STATIC_UPLOAD_FOLDER
from os.path import join

routes = Blueprint('routes', __name__)

@routes.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("routes.home"))

    return render_template("index.html", user=current_user)

@routes.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        name = request.form.get("recipeName")
        desc = request.form.get("recipeDesc")

        if not name:
            flash("Must provide a recipe name", category="error")
            return redirect(url_for("routes.home"))
        if not desc:
            flash("Must provide a recipe description", category="error")
            return redirect(url_for("routes.home"))

        photo_path = "default_recipe.png"
        if "recipePhoto" in request.files:  # check if the post request has the file part
            photo = request.files["recipePhoto"]
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if photo.filename != "" and photo.filename.endswith((".png", ".jpg", ".jpeg")):
                filename = secure_filename(photo.filename)
                photo_path = join(UPLOAD_FOLDER, filename)
                # TODO: need to check if the file is unique
                photo.save(photo_path)
                photo_path = join(STATIC_UPLOAD_FOLDER, filename)

        recipe = Recipe(name=name, desc=desc, photo_path=photo_path, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()

        return redirect(url_for("routes.home"))

    if "query" in request.args.keys():
        query = request.args["query"]
        # check recipe name and recipe description for keyword
        recipes = Recipe.query.filter(
            or_(
                Recipe.name.like(f"%{query}%"), 
                Recipe.desc.like(f"%{query}%")
            )
        ).all()
    else:
        recipes = Recipe.query.all()
    return render_template("home.html", user=current_user, recipes=recipes)

@routes.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def recipe(recipe_id):
    rec = Recipe.query.get(recipe_id)

    if request.method == "GET":
        return render_template("recipe.html", user=current_user, recipe=rec)

    if current_user.id != rec.user_id:
        abort(401)

    db.session.delete(rec)
    db.session.commit()
    return redirect(url_for("routes.home"))

@routes.route("user/<int:user_id>/recipes")
def user_recipes(user_id):
    user = User.query.get(user_id)
    return render_template("profile.html", user=current_user, recipes=user.recipes, visiting_user=user)
