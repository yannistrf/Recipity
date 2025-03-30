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

    page = 1
    if "page" in request.args.keys():
        page = int(request.args["page"])

    if "query" in request.args.keys():
        query = request.args["query"]
        # check recipe name and recipe description for keyword

        stmt = db.select(Recipe).where(
            or_(
                Recipe.name.ilike(f"%{query}%"), 
                Recipe.desc.ilike(f"%{query}%")
            )).order_by(Recipe.get_like_ratio().desc())
        recipes = db.paginate(stmt, page=page, per_page=9, error_out=False)

    else:
        recipes = db.paginate(db.select(Recipe).order_by(Recipe.get_like_ratio().desc()), page=page, per_page=9, error_out=False)
    return render_template("home.html", user=current_user, recipes=recipes)

@routes.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def recipe(recipe_id):
    rec = db.session.get(Recipe, recipe_id)

    if request.method == "GET":
        return render_template("recipe.html", user=current_user, recipe=rec)

    if current_user.id != rec.user_id:
        abort(401)

    db.session.delete(rec)
    db.session.commit()
    return redirect(url_for("routes.home"))

@routes.route("/recipe/<int:recipe_id>/like")
@login_required
def like_recipe(recipe_id):
    rec = db.session.get(Recipe, recipe_id)

    if rec not in current_user.liked_recipes:
        current_user.liked_recipes.append(rec)
        # rec.liked_by_users.append(current_user)   # same thing

        if rec in current_user.disliked_recipes:
            current_user.disliked_recipes.remove(rec)
        db.session.commit()
    else:
        current_user.liked_recipes.remove(rec)
        db.session.commit()

    return redirect(url_for("routes.recipe", recipe_id=recipe_id))

@routes.route("/recipe/<int:recipe_id>/dislike")
@login_required
def dislike_recipe(recipe_id):
    rec = db.session.get(Recipe, recipe_id)

    if rec not in current_user.disliked_recipes:
        current_user.disliked_recipes.append(rec)
        # rec.disliked_by_users.append(current_user)   # same thing
        
        if rec in current_user.liked_recipes:
            current_user.liked_recipes.remove(rec)
        db.session.commit()
    else:
        current_user.disliked_recipes.remove(rec)
        db.session.commit()

    return redirect(url_for("routes.recipe", recipe_id=recipe_id))



@routes.route("user/<int:user_id>/recipes")
@login_required
def user_recipes(user_id):
    user = db.get_or_404(User, user_id)

    page = 1
    if "page" in request.args.keys():
        page = int(request.args["page"])
    
    recipes = db.paginate(db.select(Recipe).filter_by(user_id=user_id).order_by(Recipe.get_like_ratio().desc()),
                          page=page, per_page=9, error_out=False)
    return render_template("profile.html", user=current_user, recipes=recipes, visiting_user=user)


@routes.route("/recipe/<int:recipe_id>/save")
@login_required
def save_recipe(recipe_id):
    rec = db.session.get(Recipe, recipe_id)

    if rec not in current_user.saved_recipes:
        current_user.saved_recipes.append(rec)
    else:
        current_user.saved_recipes.remove(rec)

    db.session.commit()

    return redirect(url_for("routes.recipe", recipe_id=recipe_id))

@routes.route("user/<int:user_id>/saved")
@login_required
def user_saved_recipes(user_id):

    if user_id != current_user.id:
        abort(403)

    user = db.get_or_404(User, user_id)

    page = 1
    if "page" in request.args.keys():
        page = int(request.args["page"])

    stmt = db.select(Recipe).where(Recipe.id.in_([r.id for r in user.saved_recipes])).order_by(Recipe.get_like_ratio().desc())
    saved_recipes_pagination = db.paginate(stmt, page=page, per_page=9, error_out=False)

    return render_template("saved_recipes.html", user=current_user, recipes=saved_recipes_pagination)
    