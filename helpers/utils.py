from fuzzywuzzy import fuzz
import logging

def validate_input(data):
    """Validate incoming request data."""
    if not isinstance(data, dict):
        logging.error("Invalid input: Expected a dictionary")
        return False
    if "ingredients" not in data or not isinstance(data["ingredients"], list):
        logging.error("Invalid input: 'ingredients' missing or not a list")
        return False
    return True

def score_recipe(recipe, ingredients):
    """Calculate how well a recipe matches given ingredients."""
    score = 0
    recipe_ingredients = set(recipe.get("ingredients", []))
    input_ingredients = set(ingredients)

    for ing in input_ingredients:
        best_match = max([fuzz.ratio(ing.lower(), r_ing.lower()) for r_ing in recipe_ingredients], default=0)
        score += best_match / 100
    
    return score

def log_request(request_data):
    """Log incoming API requests for debugging."""
    logging.debug(f"Received request data: {request_data}")