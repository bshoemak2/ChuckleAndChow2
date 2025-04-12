# app.py
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor
from recipe_generator import match_predefined_recipe, generate_dynamic_recipe, generate_random_recipe
from helpers import validate_input, calculate_nutrition, generate_share_text
from database import init_db, get_all_recipes
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import random

load_dotenv()

logging.basicConfig(
    filename='recipe_generator.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
CORS(app, resources={
    r"/generate_recipe": {
        "origins": [
            "http://localhost:8080",
            "http://localhost:8081",
            "https://recipegenerator-ort9.onrender.com",
            "https://recipegenerator-frontend.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Origin"]
    }
}, supports_credentials=True)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "10 per minute"],
    storage_uri="memory://"
)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
executor = ThreadPoolExecutor(max_workers=4)

try:
    init_db()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database: {str(e)}")

ALL_RECIPES = get_all_recipes()
logging.debug(f"Loaded {len(ALL_RECIPES)} recipes from database: {ALL_RECIPES}")
if not ALL_RECIPES:
    logging.warning("No recipes found in database; falling back to dynamic generation")

def score_recipe(recipe, ingredients, preferences):
    score = 0
    if not recipe or 'ingredients' not in recipe:
        return 0
    if ingredients:
        recipe_ingredients = set()
        if recipe['ingredients']:
            if isinstance(recipe['ingredients'][0], (tuple, list)):
                recipe_ingredients = {item for _, item in recipe['ingredients']}
            else:
                recipe_ingredients = set(recipe['ingredients'])
        input_ingredients = set(ingredients)
        for input_ing in input_ingredients:
            best_match = max(
                [fuzz.ratio(input_ing.lower(), r_ing.lower()) for r_ing in recipe_ingredients],
                default=0
            )
            score += best_match / 100
    if preferences.get('diet') and preferences['diet'].lower() in recipe.get('diet', '').lower():
        score += 0.5
    if preferences.get('time') and preferences['time'].lower() in recipe.get('cooking_time', '').lower():
        score += 0.3
    return score

@app.route('/generate_recipe', methods=['POST', 'OPTIONS'])
@limiter.limit("10 per minute")
@cache.cached(timeout=3600, key_prefix=lambda: f"recipe_{request.get_json(silent=True).get('preferences', {}).get('isRandom', False)}_{sorted(request.get_json(silent=True).get('ingredients', []))}")
def generate_recipe():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValueError("Invalid JSON payload")
        ingredients = data.get('ingredients', [])
        preferences = data.get('preferences', {})
        logging.debug(f"Extracted inputs: ingredients={ingredients}, preferences={preferences}")

        if not isinstance(ingredients, list) or not isinstance(preferences, dict):
            raise ValueError("Ingredients must be a list and preferences a dict")
        
        language = preferences.get('language', 'english').lower()
        is_random = preferences.get('isRandom', False)

        def process_recipe(recipe):
            if not recipe or "error" in recipe or not isinstance(recipe, dict) or 'ingredients' not in recipe:
                logging.debug(f"Invalid recipe object: {recipe}")
                return None
            try:
                # Normalize title and steps based on language
                recipe['title'] = recipe.get(f'title_{language}', recipe.get('title_en', 'Untitled'))
                recipe['steps'] = recipe.get(f'steps_{language}', recipe.get('steps_en', recipe.get('steps', [])))
                # Normalize ingredients to strings
                if recipe['ingredients']:
                    if isinstance(recipe['ingredients'][0], (tuple, list)):
                        ingredients_list = sorted([f"{qty} {item}" if qty else item for qty, item in recipe['ingredients']], key=lambda x: x.split()[1])
                        nutrition_items = [item for qty, item in recipe['ingredients']]
                    else:
                        ingredients_list = sorted([str(item) for item in recipe['ingredients']])
                        nutrition_items = recipe['ingredients']
                    recipe['ingredients'] = ingredients_list
                else:
                    recipe['ingredients'] = []
                    nutrition_items = []
                # Generate title after flattening ingredients
                if recipe['title'] == 'Untitled' and recipe['ingredients']:
                    title_parts = [item.split()[-1].capitalize() for item in recipe['ingredients'][:2]]  # Use last part (ingredient name)
                    recipe['title'] = f"{' and '.join(title_parts)} Skillet"
                nutrition_future = executor.submit(calculate_nutrition, nutrition_items) if nutrition_items else None
                share_text = generate_share_text(recipe, language, is_predefined=not is_random)
                recipe['nutrition'] = recipe.get('nutrition', nutrition_future.result() if nutrition_future else {"calories": 0})
                recipe['shareText'] = share_text
                # Clean up extra fields
                for key in ['title_en', 'title_es', 'steps_en', 'steps_es']:
                    recipe.pop(key, None)
                return recipe
            except Exception as e:
                logging.error(f"Error processing recipe: {str(e)}", exc_info=True)
                return None

        if is_random:
            if ALL_RECIPES:
                valid_recipes = [r for r in ALL_RECIPES if isinstance(r, dict) and 'ingredients' in r and ('title_en' in r or 'title_es' in r)]
                logging.debug(f"Found {len(valid_recipes)} valid recipes out of {len(ALL_RECIPES)}: {valid_recipes}")
                if valid_recipes:
                    scored_recipes = [(r, score_recipe(r, ingredients, preferences)) for r in valid_recipes]
                    top_recipes = sorted(scored_recipes, key=lambda x: x[1], reverse=True)[:5]
                    recipe = random.choice([r for r, _ in top_recipes])
                    logging.debug(f"Selected random recipe from ALL_RECIPES: {recipe}")
                else:
                    logging.debug("No valid recipes in ALL_RECIPES; falling back to generate_random_recipe")
                    recipe = generate_random_recipe(language)
            else:
                logging.debug("No ALL_RECIPES; using generate_random_recipe")
                recipe = generate_random_recipe(language)
            processed_recipe = process_recipe(recipe)
            if not processed_recipe:
                logging.warning("Random recipe failed; falling back to dynamic generation")
                recipe = generate_dynamic_recipe([], preferences)
                processed_recipe = process_recipe(recipe)
                if not processed_recipe:
                    logging.error(f"Failed to generate fallback dynamic recipe: {recipe}")
                    return jsonify({"error": "No recipes available"}), 500
            logging.info(f"Generated random recipe: {processed_recipe['title']}")
            return jsonify(processed_recipe)

        if ingredients:
            recipe = match_predefined_recipe(ingredients, language)
            logging.debug(f"Match predefined recipe result: {recipe}")
            if recipe:
                processed_recipe = process_recipe(recipe)
                if processed_recipe:
                    logging.info(f"Matched predefined recipe: {processed_recipe['title']}")
                    return jsonify(processed_recipe)

        recipe = generate_dynamic_recipe(ingredients, preferences)
        logging.debug(f"Dynamic recipe result: {recipe}")
        processed_recipe = process_recipe(recipe)
        if not processed_recipe:
            logging.error(f"Failed to generate dynamic recipe: {recipe}")
            return jsonify({"error": "Recipe generation failed"}), 500
        logging.info(f"Generated dynamic recipe: {processed_recipe['title']}")
        return jsonify(processed_recipe)

    except ValueError as ve:
        logging.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error(f"Unexpected error in generate_recipe: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)