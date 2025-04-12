from flask import request, jsonify
from config import app, limiter, cache
from services.recipe_service import generate_recipe_service
from services.ingredient_service import get_ingredients_service

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Chuckle & Chow Recipe API—Where Food Meets Funny!",
        "endpoints": {
            "/ingredients": "GET - Grab some grub options",
            "/generate_recipe": "POST - Cook up a laugh riot (send ingredients and preferences)",
        },
        "status": "cookin’ and jokin’",
    })

@app.route("/ingredients", methods=["GET", "OPTIONS"])
@limiter.limit("50 per day")
def get_ingredients():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify(get_ingredients_service())

@app.route("/generate_recipe", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")
def generate_recipe():
    if request.method == "OPTIONS":
        return "", 200
    return generate_recipe_service(request)