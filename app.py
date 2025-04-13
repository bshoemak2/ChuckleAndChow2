import logging
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from recipe_generator import match_predefined_recipe, generate_dynamic_recipe, generate_random_recipe
from helpers import validate_input, calculate_nutrition, generate_share_text
from database import init_db, get_all_recipes
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import random

# Configure logging
logging.basicConfig(
    filename='recipe_generator.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
    force=True
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console_handler)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)
werkzeug_logger.propagate = False

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
CORS(app, resources={
    r"/generate_recipe": {"origins": ["*"], "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Origin"]},
    r"/ingredients": {"origins": ["*"], "methods": ["GET", "OPTIONS"], "allow_headers": ["Content-Type", "Origin"]},
    r"/api": {"origins": ["*"], "methods": ["GET"]}
}, supports_credentials=True)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day", "20 per minute"], storage_uri="memory://")
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
executor = ThreadPoolExecutor(max_workers=4)

try:
    init_db()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database: {str(e)}", exc_info=True)

ALL_RECIPES = get_all_recipes()
logging.debug(f"Loaded {len(ALL_RECIPES)} recipes from database: {ALL_RECIPES[:2] if ALL_RECIPES else []}")
if not ALL_RECIPES or not isinstance(ALL_RECIPES, list):
    logging.warning("ALL_RECIPES is invalid or empty; falling back to dynamic generation")
    ALL_RECIPES = []

COOKING_METHODS = ["Grill", "Fry", "Bake", "Boil", "Sauté", "Roast", "Simmer"]
EQUIPMENT_OPTIONS = ["skillet", "pot", "grill", "oven", "mixing bowl", "tongs", "spatula", "knife"]
EQUIPMENT_QUIRKY = ["busted spatula", "rusty tongs", "haunted whisk"]
FUNNY_PREFIXES = ["Redneck", "Drunk", "Hillbilly", "Bubba’s", "Sassy Granny’s", "Bootleg", "Yeehaw"]
FUNNY_SUFFIXES = ["Fry", "Hoedown", "Feast", "Supper", "Brawl"]
SPICES_AND_EXTRAS = ["1 tsp salt", "1/2 tsp black pepper", "1 tbsp paprika", "1 tsp garlic powder", "1 tbsp hot sauce", "1 tbsp oil"]
CHAOS_TIPS = ["Spill a splash of beer for extra sizzle!", "Holler at it to tenderize!", "Bribe the neighbors with a plate if they sniff around!"]
INSULTS = ["Tastier than roadkill!", "Even yer cousin’d eat it!", "Good enough for the barn!"]

INGREDIENT_PAIRS = {
    "ground beef": ["beer", "onion", "cheese"],
    "chicken": ["lemon", "butter", "rice"],
    "pork": ["apple", "whiskey", "potato"],
    "salmon": ["lemon", "butter", "vodka"],
    "moonshine": ["ground beef", "pork", "chicken"],
    "beer": ["ground beef", "chicken", "bread"]
}

METHOD_PREFERENCES = {
    "tequila": ["Grill"],
    "moonshine": ["Fry"],
    "beer": ["Simmer"],
    "ground beef": ["Fry"]
}

RECIPE_TEMPLATES = [
    [
        "Prep: Chop {ingredients} into bite-sized pieces—mind yer fingers!",
        "Cook: {method} in {equipment} over {heat} for {time}, stirrin’ like yer wranglin’ a hog.",
        "Serve: Plate with {extra}, prouder’n a rooster at dawn."
    ],
    [
        "Start: Mix {ingredients} with {extra} in a {equipment}.",
        "Heat: {method} over {heat} for {time}, flippin’ like yer dodgin’ a skunk.",
        "Finish: Serve hot with cornbread or salad—holler when it’s ready!"
    ]
]

def score_recipe(recipe, ingredients, preferences):
    score = 0
    if not recipe or 'ingredients' not in recipe:
        return 0
    if ingredients:
        recipe_ingredients = set()
        if recipe['ingredients']:
            if isinstance(recipe['ingredients'][0], (tuple, list)):
                recipe_ingredients = {item[0] if isinstance(item, (tuple, list)) else item for item in recipe['ingredients']}
            else:
                recipe_ingredients = set(recipe['ingredients'])
        input_ingredients = set(ingredients)
        for input_ing in input_ingredients:
            best_match = max([fuzz.ratio(input_ing.lower(), r_ing.lower()) for r_ing in recipe_ingredients], default=0)
            score += best_match / 100
            if input_ing in INGREDIENT_PAIRS:
                for paired in INGREDIENT_PAIRS[input_ing]:
                    if paired in recipe_ingredients:
                        score += 0.2
    return score

AMAZON_ASINS = {
    "ground beef": "B08J4K9L2P",
    "chicken": "B07Z8J9K7L",
    "pork": "B09J8K9M2P",
    "squirrel": "B07K9M8N2P",
}

def process_recipe(recipe):
    try:
        logging.debug(f"Starting process_recipe with input: {recipe}")
        input_ingredients = recipe.get('input_ingredients', recipe.get('ingredients', []))
        # Use recipe['ingredients'] if input_ingredients is empty
        if not input_ingredients and 'ingredients' in recipe:
            input_ingredients = recipe['ingredients']
        
        method = random.choice(COOKING_METHODS)
        for ing in input_ingredients:
            if ing in METHOD_PREFERENCES:
                method = random.choice(METHOD_PREFERENCES[ing] + [method])
        
        prefix = random.choice(FUNNY_PREFIXES)
        suffix = random.choice(FUNNY_SUFFIXES)
        extras = random.sample(SPICES_AND_EXTRAS, k=random.randint(1, 2))
        extra_text = f"{', '.join(extras)}" if extras else "a pinch of salt"
        
        # Realistic ingredients with varied measurements
        measurements = {
            "meat": ["1 lb", "cubed"],
            "vegetables": ["2 medium", "diced"],
            "fruits": ["1 cup", "sliced"],
            "seafood": ["1 lb", "cleaned"],
            "dairy": ["2 tbsp", "melted"],
            "bread_carbs": ["1 cup", "cooked"],
            "devil_water": ["1/2 cup", ""]
        }
        ingredients_list = []
        nutrition_items = []
        for ing in input_ingredients:
            meas = "1 unit"
            prep = ""
            for cat, items in INGREDIENT_CATEGORIES.items():
                if ing in [item['name'] for item in items]:
                    meas, prep = measurements.get(cat, ["1 unit", ""])
                    break
            ingredients_list.append(f"{meas} {ing}" + (f", {prep}" if prep else ""))
            nutrition_items.append(ing)
        if not ingredients_list:
            ingredients_list = ["1 unit unknown grub"]
            nutrition_items = ["unknown"]
        ingredients_list.append("1 tbsp oil, for cooking")  # Add practical oil
        
        title_items = [ing.split()[-1].capitalize() for ing in ingredients_list if "oil" not in ing][:2] or ["Mystery"]
        recipe['title'] = f"{prefix} {method} {' and '.join(title_items)} {suffix}"
        
        recipe['ingredients_with_links'] = [
            {"name": ing, "url": f"https://www.amazon.com/dp/{AMAZON_ASINS.get(ing.split()[-1], 'B08J4K9L2P')}?tag=bshoemak-20"}
            for ing in ingredients_list
        ]
        recipe['add_all_to_cart'] = f"https://www.amazon.com/gp/aws/cart/add.html?AssociateTag=bshoemak-20&" + "&".join(
            [f"ASIN.{i+1}={AMAZON_ASINS.get(ing.split()[-1], 'B08J4K9L2P')}&Quantity.{i+1}=1" for i, ing in enumerate(ingredients_list)]
        )
        
        equipment = random.sample(EQUIPMENT_OPTIONS, k=3)
        quirky_gear = random.choice(EQUIPMENT_QUIRKY)
        primary_equipment = equipment[0]
        
        chaos_tip = random.choice(CHAOS_TIPS)
        insult = random.choice(INSULTS)
        
        steps_key = 'steps'
        heat = "medium heat"
        time = "8-12 minutes"
        if method in ["Grill", "Fry", "Sauté"]:
            heat = "medium-high heat"
            time = "6-10 minutes"
        elif method == "Bake":
            heat = "350°F"
            time = "15-20 minutes"
        elif method == "Boil":
            heat = "boiling water"
            time = "10-15 minutes"
        
        if steps_key in recipe and recipe[steps_key] and len(recipe[steps_key]) >= 3:
            recipe['steps'] = [
                f"Prep: {recipe[steps_key][0].replace('Cook', 'Chop or prep')}.",
                f"{method} in {primary_equipment} over {heat} for {time}, stirring occasionally.",
                f"Serve hot with {extra_text} and a side of cornbread or salad. {insult}"
            ]
        else:
            template = random.choice(RECIPE_TEMPLATES)
            logging.debug(f"Using template: {template}")
            recipe['steps'] = [
                template[0].format(ingredients=' and '.join(ingredients_list[:2]), extra=extra_text, equipment=primary_equipment),
                template[1].format(method=method.lower(), equipment=primary_equipment, heat=heat, time=time),
                template[2].format(**({'extra': extra_text} if '{extra}' in template[2] else {})) + f" {insult}"
            ]
        
        recipe['steps'].append(f"Chaos Tip: {chaos_tip}")
        recipe['ingredients'] = ingredients_list
        recipe['equipment'] = equipment
        recipe['chaos_gear'] = quirky_gear
        
        # Realistic nutrition
        nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for item in nutrition_items:
            if item in [i['name'] for i in INGREDIENT_CATEGORIES['meat'] + INGREDIENT_CATEGORIES['seafood']]:
                nutrition["calories"] += 800
                nutrition["protein"] += 60
                nutrition["fat"] += 40
            elif item in [i['name'] for i in INGREDIENT_CATEGORIES['vegetables']]:
                nutrition["calories"] += 100
                nutrition["carbs"] += 20
            elif item in [i['name'] for i in INGREDIENT_CATEGORIES['bread_carbs']]:
                nutrition["calories"] += 200
                nutrition["carbs"] += 40
            elif item in [i['name'] for i in INGREDIENT_CATEGORIES['dairy']]:
                nutrition["calories"] += 150
                nutrition["fat"] += 10
            elif item in [i['name'] for i in INGREDIENT_CATEGORIES['fruits']]:
                nutrition["calories"] += 80
                nutrition["carbs"] += 15
            elif item in [i['name'] for i in INGREDIENT_CATEGORIES['devil_water']]:
                nutrition["calories"] += 100
        nutrition["calories"] = max(100, nutrition["calories"])  # Ensure non-zero
        nutrition["chaos_factor"] = 7
        recipe['nutrition'] = nutrition
        
        recipe['shareText'] = f"Behold my culinary chaos: {recipe['title']}\nGear: {', '.join(equipment)}\nChaos Gear: {quirky_gear}\nGrub: {', '.join(ingredients_list)}\nSteps:\n{' '.join(recipe['steps'])}\nCalories: {recipe['nutrition']['calories']} (Chaos: {recipe['nutrition']['chaos_factor']}/10)"
        
        # Remove all Spanish fields
        for key in ['title_es', 'steps_es']:
            recipe.pop(key, None)
        
        logging.debug(f"Processed recipe successfully: {recipe}")
        return recipe
    except Exception as e:
        logging.error(f"Error processing recipe: {str(e)}", exc_info=True)
        return {"title": "Error Recipe", "ingredients": [], "steps": ["Something went wrong!"], "nutrition": {"calories": 0}}

# Temporary mock fallback for generate_random_recipe
def generate_random_recipe(language='english'):
    logging.debug("Using fallback generate_random_recipe")
    try:
        # Mock a simple random recipe
        ingredients = random.sample(
            [item['name'] for cat in INGREDIENT_CATEGORIES.values() for item in cat],
            k=3
        )
        recipe = {
            'title_en': 'Random Chaos Dish',
            'ingredients': ingredients,
            'steps': [
                f"Prep: Chop {ingredients[0]} and {ingredients[1]}.",
                f"Cook: {random.choice(COOKING_METHODS)} everything together.",
                "Serve: Enjoy with a side of chaos!"
            ],
            'nutrition': {'calories': 500}
        }
        logging.debug(f"Fallback recipe generated: {recipe}")
        return recipe
    except Exception as e:
        logging.error(f"Fallback generate_random_recipe failed: {str(e)}")
        return None

INGREDIENT_CATEGORIES = {
    "meat": sorted([
        {"name": "ground beef", "category": "meat"},
        {"name": "chicken", "category": "meat"},
        {"name": "pork", "category": "meat"},
        {"name": "lamb", "category": "meat"},
        {"name": "pichana", "category": "meat"},
        {"name": "churrasco", "category": "meat"},
        {"name": "ribeye steaks", "category": "meat"},
        {"name": "squirrel", "category": "meat"},
        {"name": "rabbit", "category": "meat"},
        {"name": "quail", "category": "meat"},
        {"name": "woodpecker", "category": "meat"}
    ], key=lambda x: x["name"]),
    "vegetables": sorted([
        {"name": "cauliflower", "category": "vegetables"},
        {"name": "carrot", "category": "vegetables"},
        {"name": "broccoli", "category": "vegetables"},
        {"name": "onion", "category": "vegetables"},
        {"name": "potato", "category": "vegetables"},
        {"name": "tomato", "category": "vegetables"},
        {"name": "green beans", "category": "vegetables"},
        {"name": "okra", "category": "vegetables"},
        {"name": "collards", "category": "vegetables"}
    ], key=lambda x: x["name"]),
    "fruits": sorted([
        {"name": "apple", "category": "fruits"},
        {"name": "banana", "category": "fruits"},
        {"name": "lemon", "category": "fruits"},
        {"name": "orange", "category": "fruits"},
        {"name": "mango", "category": "fruits"},
        {"name": "avocado", "category": "fruits"},
        {"name": "starfruit", "category": "fruits"},
        {"name": "dragon fruit", "category": "fruits"},
        {"name": "carambola", "category": "fruits"}
    ], key=lambda x: x["name"]),
    "seafood": sorted([
        {"name": "salmon", "category": "seafood"},
        {"name": "shrimp", "category": "seafood"},
        {"name": "cod", "category": "seafood"},
        {"name": "tuna", "category": "seafood"},
        {"name": "yellowtail snapper", "category": "seafood"},
        {"name": "grouper", "category": "seafood"},
        {"name": "red snapper", "category": "seafood"},
        {"name": "oysters", "category": "seafood"},
        {"name": "lobster", "category": "seafood"},
        {"name": "conch", "category": "seafood"},
        {"name": "lionfish", "category": "seafood"},
        {"name": "catfish", "category": "seafood"},
        {"name": "bass", "category": "seafood"},
        {"name": "crappie", "category": "seafood"}
    ], key=lambda x: x["name"]),
    "dairy": sorted([
        {"name": "cheese", "category": "dairy"},
        {"name": "milk", "category": "dairy"},
        {"name": "butter", "category": "dairy"},
        {"name": "yogurt", "category": "dairy"},
        {"name": "eggs", "category": "dairy"}
    ], key=lambda x: x["name"]),
    "bread_carbs": sorted([
        {"name": "bread", "category": "bread_carbs"},
        {"name": "pasta", "category": "bread_carbs"},
        {"name": "rice", "category": "bread_carbs"},
        {"name": "tortilla", "category": "bread_carbs"}
    ], key=lambda x: x["name"]),
    "devil_water": sorted([
        {"name": "beer", "category": "devil_water"},
        {"name": "moonshine", "category": "devil_water"},
        {"name": "whiskey", "category": "devil_water"},
        {"name": "vodka", "category": "devil_water"},
        {"name": "tequila", "category": "devil_water"}
    ], key=lambda x: x["name"])
}

@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        "message": "Welcome to the Chuckle & Chow Recipe API—Where Food Meets Funny!",
        "endpoints": {
            "/ingredients": "GET - Grab some grub options",
            "/generate_recipe": "POST - Cook up a laugh riot (send ingredients and preferences)"
        },
        "status": "cookin’ and jokin’"
    })

@app.route('/ingredients', methods=['GET', 'OPTIONS'])
@limiter.limit("50 per day")
def get_ingredients():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({k: [item['name'] for item in v] for k, v in INGREDIENT_CATEGORIES.items()})

def get_cache_key():
    data = request.get_json(silent=True) or {}
    is_random = data.get('preferences', {}).get('isRandom', False)
    ingredients = sorted(data.get('ingredients', []))
    return f"recipe_{is_random}_{ingredients}"

@app.route('/generate_recipe', methods=['POST', 'OPTIONS'])
@limiter.limit("20 per minute")
@cache.cached(timeout=3600, key_prefix=get_cache_key)
def generate_recipe():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        raw_data = request.get_data(as_text=True)
        logging.debug(f"Raw request data: {raw_data}")
        
        data = request.get_json(silent=True)
        if data is None:
            logging.error("Failed to parse JSON: invalid or missing payload")
            return jsonify({"error": "Invalid or missing JSON payload—check your request format!"}), 400
        if not isinstance(data, dict):
            logging.error(f"Parsed data is not a dict: {data}")
            return jsonify({"error": "Payload must be a JSON object—not an array or string!"}), 400
        
        ingredients = data.get('ingredients', [])
        preferences = data.get('preferences', {})
        logging.debug(f"Extracted inputs: ingredients={ingredients}, preferences={preferences}")
        if not isinstance(ingredients, list):
            return jsonify({"error": "Ingredients must be a list"}), 400
        if not isinstance(preferences, dict):
            return jsonify({"error": "Preferences must be a dict"}), 400
        
        is_random = preferences.get('isRandom', False)
        style = preferences.get('style', '')
        category = preferences.get('category', '')
        logging.debug(f"Processing with: is_random={is_random}, style={style}, category={category}")

        def process_and_enrich_recipe(recipe):
            logging.debug(f"Processing recipe: {recipe}")
            processed = process_recipe({**recipe, 'input_ingredients': ingredients})
            if not processed or not isinstance(processed, dict):
                logging.warning("process_recipe returned invalid data; using fallback")
                processed = {"title": "Fallback Recipe", "ingredients": [], "steps": ["Try again later!"], "nutrition": {"calories": 0}}
            if style:
                processed['title'] = f"{processed['title']} ({style})"
            if category:
                processed['title'] = f"{processed['title']} - {category}"
            return processed

        if is_random:
            logging.debug("Generating random recipe")
            logging.debug(f"ALL_RECIPES length: {len(ALL_RECIPES)}, sample: {ALL_RECIPES[:2] if ALL_RECIPES else []}")
            if not ALL_RECIPES:
                logging.warning("ALL_RECIPES is empty; falling back to generate_random_recipe")
                recipe = generate_random_recipe('english')
                logging.debug(f"Generated random recipe: {recipe}")
            else:
                valid_recipes = [r for r in ALL_RECIPES if isinstance(r, dict) and 'ingredients' in r and 'title_en' in r]
                logging.debug(f"Found {len(valid_recipes)} valid recipes out of {len(ALL_RECIPES)}")
                if not valid_recipes:
                    logging.warning("No valid recipes in ALL_RECIPES; using generate_random_recipe")
                    recipe = generate_random_recipe('english')
                    logging.debug(f"Generated random recipe: {recipe}")
                else:
                    scored_recipes = [(r, score_recipe(r, ingredients, preferences)) for r in valid_recipes]
                    top_recipes = sorted(scored_recipes, key=lambda x: x[1], reverse=True)[:5]
                    recipe = random.choice([r for r, _ in top_recipes])
                    logging.debug(f"Selected random recipe from ALL_RECIPES: {recipe}")
            if not recipe or not isinstance(recipe, dict):
                logging.error(f"Invalid recipe generated: {recipe}")
                return jsonify({"error": "Failed to generate a valid random recipe"}), 500
            processed_recipe = process_and_enrich_recipe(recipe)
            logging.info(f"Generated random recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
            return jsonify(processed_recipe)

        if ingredients:
            logging.debug("Matching predefined recipe")
            recipe = match_predefined_recipe(ingredients, 'english')
            logging.debug(f"Match predefined recipe result: {recipe}")
            if recipe:
                processed_recipe = process_and_enrich_recipe(recipe)
                logging.info(f"Matched predefined recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
                return jsonify(processed_recipe)

        logging.debug("Generating dynamic recipe")
        recipe = generate_dynamic_recipe(ingredients, preferences)
        logging.debug(f"Dynamic recipe result: {recipe}")
        processed_recipe = process_and_enrich_recipe(recipe)
        if not processed_recipe:
            logging.error(f"Failed to generate dynamic recipe: {recipe}", exc_info=True)
            return jsonify({"error": "Recipe generation flopped—blame the chef!"}), 500
        logging.info(f"Generated dynamic recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
        return jsonify(processed_recipe)

    except Exception as e:
        logging.error(f"Unexpected error in generate_recipe: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}—check the logs!"}), 500

# Serve React frontend for non-API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    logging.debug(f"Current working directory: {os.getcwd()}")
    logging.debug(f"Checking build directory: build")
    build_dir = 'build'
    logging.debug(f"Attempting to serve frontend for path: {path or 'index.html'}")
    if path and (path.startswith('generate_recipe') or path.startswith('ingredients') or path.startswith('api')):
        logging.debug(f"Routing to API: {path}")
        return app.send_static_file(path)  # Let Flask handle API routes
    try:
        if not os.path.exists(build_dir):
            logging.error(f"Build directory not found: {build_dir}")
            return jsonify({"error": "Frontend build not found. Please check build process."}), 500
        file_path = path or 'index.html'
        logging.debug(f"Serving file: {os.path.join(build_dir, file_path)}")
        return send_from_directory(build_dir, file_path)
    except FileNotFoundError as e:
        logging.error(f"File not found: {os.path.join(build_dir, file_path)} - {str(e)}")
        if file_path != 'index.html':
            logging.debug("Falling back to index.html for SPA routing")
            return send_from_directory(build_dir, 'index.html')
        return jsonify({"error": f"Frontend index.html not found in {build_dir}. Please check build process."}), 500
    except Exception as e:
        logging.error(f"Error serving frontend: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to serve frontend: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)