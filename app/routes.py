from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_
from .models import Recipe
from . import db

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

        recipe = Recipe(name=name, desc=desc, user_id=current_user.id)
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
