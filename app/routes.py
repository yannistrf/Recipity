from flask import Blueprint, render_template, request, redirect, url_for
from .models import Recipe
from . import db

routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("recipeName")
        desc = request.form.get("recipeDesc")

        recipe = Recipe(name=name, desc=desc)
        db.session.add(recipe)
        db.session.commit()

        return redirect(url_for("routes.home"))

    recipes = Recipe.query.all()
    return render_template("home.html", recipes=recipes)
