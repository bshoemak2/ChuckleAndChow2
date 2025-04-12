# app.py
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from recipe_generator import match_predefined_recipe, generate_dynamic_recipe, generate_random_recipe
from helpers import validate_input, calculate_nutrition, generate_share_text
from database import init_db, get_all_recipes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename='recipe_generator.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
}, supports_credentials=True)  # Ensure CORS headers are sent

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "10 per minute"],
    storage_uri="memory://"
)

try:
    init_db()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database: {str(e)}")

@app.route('/generate_recipe', methods=['POST', 'OPTIONS'])
@limiter.limit("10 per minute")
def generate_recipe():
    if request.method == 'OPTIONS':
        return '', 200  # Handle preflight explicitly

    try:
        logging.debug(f"Raw request JSON: {request.json}")
        data = request.json
        ingredients = data.get('ingredients', [])
        preferences = data.get('preferences', {})
        logging.debug(f"Extracted inputs: ingredients={ingredients}, preferences={preferences}")
        
        language = preferences.get('language', 'english').lower()
        is_random = preferences.get('isRandom', False)

        if is_random:
            recipe = generate_random_recipe(language)
            if not recipe or "error" in recipe:
                logging.error(f"Failed to generate random recipe: {recipe.get('error', 'Unknown error')}")
                return jsonify({"error": recipe.get('error', "No recipes available")}), 500
            recipe['ingredients'] = sorted([f"{qty} {item}" for item, qty in recipe['ingredients']]) if recipe['ingredients'] else []
            share_text = generate_share_text(recipe, language, is_predefined=True)
            logging.info(f"Generated random recipe: {recipe['title']}")
            return jsonify({
                "id": recipe['id'],
                "title": recipe['title'],
                "ingredients": recipe['ingredients'],
                "steps": recipe['steps'],
                "nutrition": recipe['nutrition'],
                "cooking_time": recipe['cooking_time'],
                "difficulty": recipe['difficulty'],
                "equipment": recipe['equipment'],
                "servings": recipe['servings'],
                "tips": recipe['tips'],
                "shareText": share_text
            })

        if ingredients:
            recipe = match_predefined_recipe(ingredients, language)
            if recipe:
                recipe['ingredients'] = sorted([f"{qty} {item}" for item, qty in recipe['ingredients']]) if recipe['ingredients'] else []
                share_text = generate_share_text(recipe, language, is_predefined=True)
                logging.info(f"Matched predefined recipe: {recipe['title']}")
                return jsonify({
                    "id": recipe['id'],
                    "title": recipe['title'],
                    "ingredients": recipe['ingredients'],
                    "steps": recipe['steps'],
                    "nutrition": recipe['nutrition'],
                    "cooking_time": recipe['cooking_time'],
                    "difficulty": recipe['difficulty'],
                    "equipment": recipe['equipment'],
                    "servings": recipe['servings'],
                    "tips": recipe['tips'],
                    "shareText": share_text
                })

        recipe = generate_dynamic_recipe(ingredients, preferences)
        recipe['nutrition'] = calculate_nutrition([item for item, qty in recipe['ingredients']]) if recipe['ingredients'] else {"calories": 0}
        recipe['ingredients'] = sorted([f"{qty} {item}" for item, qty in recipe['ingredients']]) if recipe['ingredients'] else []
        share_text = generate_share_text(recipe, language)
        logging.info(f"Generated dynamic recipe: {recipe['title']}")
        return jsonify(recipe)

    except Exception as e:
        logging.error(f"Error in generate_recipe endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)