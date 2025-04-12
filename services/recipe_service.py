import logging
import random
from flask import jsonify
from database import get_all_recipes
from recipe_generator import match_predefined_recipe, generate_dynamic_recipe, generate_random_recipe
from helpers.utils import validate_input, score_recipe
from helpers.nutrition import calculate_nutrition

ALL_RECIPES = get_all_recipes()

def generate_recipe_service(request):
    try:
        data = request.get_json(silent=True) or {}
        ingredients = data.get("ingredients", [])
        preferences = data.get("preferences", {})

        if not ingredients:
            return jsonify({"error": "Ingredients are required!"}), 400
        
        if preferences.get("isRandom"):
            recipe = generate_random_recipe(preferences.get("language", "english"))
        else:
            recipe = match_predefined_recipe(ingredients, preferences.get("language", "english"))
        
        if not recipe:
            recipe = generate_dynamic_recipe(ingredients, preferences)

        processed_recipe = process_recipe(recipe)
        logging.info(f"Generated recipe: {processed_recipe.get('title', 'Unnamed Recipe')}")
        return jsonify(processed_recipe)

    except Exception as e:
        logging.error(f"Error generating recipe: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while generating the recipe!"}), 500