import logging
import os
from flask import Flask, request, jsonify
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
    r"/": {"origins": ["*"], "methods": ["GET"]}
}, supports_credentials=True)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day", "10 per minute"], storage_uri="memory://")
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
executor = ThreadPoolExecutor(max_workers=4)

try:
    init_db()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database: {str(e)}", exc_info=True)

ALL_RECIPES = get_all_recipes()
logging.debug(f"Loaded {len(ALL_RECIPES)} recipes from database: {ALL_RECIPES}")
if not ALL_RECIPES or not isinstance(ALL_RECIPES, list):
    logging.warning("ALL_RECIPES is invalid or empty; falling back to dynamic generation")
    ALL_RECIPES = []

COOKING_METHODS = ["Burn", "Chuck", "Sizzle", "Holler At", "Wrestle", "Smack", "Yeet", "Flamethrower", "Mud-Boil", "Hog-Roast"]
EQUIPMENT_OPTIONS = ["rusty skillet", "dent dented pot", "old boot", "grandma's flip-flop", "truck hood", "banjo", "shotgun barrel", "coon trap"]
EQUIPMENT_PREFIXES = ["wrecked", "cursed", "busted", "haunted"]
FUNNY_PREFIXES = ["Redneck", "Drunk", "Hillbilly", "Limping Eagle's", "Caveman", "Sassy Granny's", "Bootleg", "Yeehaw", "Bubba’s"]
FUNNY_SUFFIXES = ["Pudding", "Surprise", "Mess", "Stew", "Disaster", "Holler", "Slop", "Gut-Buster", "Hoedown"]
SPICES_AND_EXTRAS = ["pinch of chaos", "hog grease", "swamp salt", "coon pepper", "moonshine splash", "granny’s secret dust", "beer foam", "barley belch"]
CHAOS_EVENTS = ["Coon steals half yer grub—double the beer!", "Granny’s curse: add a shot of moonshine!", "Truck backfires—extra char on that meat!", "Spill half yer beer on yer boots—cook faster!"]
DISASTERS = ["Fire starts—yell louder!", "Skillet explodes—keep cookin’!", "Beer fizzes over—laugh it off!"]
AFTERMATHS = ["Cops show up—hide the beer!", "Gator smells it—run!", "Neighbors complain—eat faster!"]
SINGULARITIES = ["Everything fuses into a mystery blob—eat it raw!", "Recipe implodes—start over!", "Chaos wins—abandon hope!"]
RESURRECTIONS = ["{gear} rises from the ashes—use it again!", "{gear} reforms with a vengeance!", "{gear} ain’t done yet!"]
TIME_WARPS = ["Two hours vanish—where’d the beef go?", "Time skips—beer’s gone flat!", "Clock breaks—cook forever!"]
NONSENSE = ["Yell, scream, and dance while it cooks!", "Sing a banjo tune to it!", "Punch the air ‘til it’s done!"]
INSULTS = ["Fit for a hog’s ass!", "Tastier than roadkill!", "Even yer cousin’d eat it!", "Good enough for the outhouse!", "Even a hog’d spit this out!", "Yer dog’d bury it!"]

INGREDIENT_PAIRS = {
    "ground beef": ["beer", "onion", "cheese"],
    "chicken": ["lemon", "butter", "rice"],
    "pork": ["apple", "whiskey", "potato"],
    "salmon": ["lemon", "butter", "vodka"],
    "moonshine": ["ground beef", "pork", "chicken"],
    "beer": ["ground beef", "chicken", "bread"]
}

METHOD_PREFERENCES = {
    "tequila": ["Flamethrower"],
    "moonshine": ["Flamethrower", "Mud-Boil"],
    "beer": ["Mud-Boil", "Sizzle"],
    "ground beef": ["Hog-Roast", "Sizzle"]
}

RECIPE_TEMPLATES = [
    ["Prep: Toss {ingredients} in like it’s a bar fight.", "Cook: {method} it in {equipment} ‘til it hollers back.", "Finish: Slap on {extra} and serve with a grunt."],
    ["Start: Mix {ingredients} with {extra} like a moonshine mash.", "Simmer: {method} it low in {equipment} ‘til it’s thick as mud.", "Serve: Dish it up hot and ornery."],
    ["Gather: Chuck {ingredients} into {equipment} with a holler.", "Blast: {method} it hard ‘til it’s kickin’ like a mule.", "Plate: Drizzle {extra} and call it supper."]
]

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
        language = recipe.get('language', 'english')
        input_ingredients = recipe.get('input_ingredients', recipe.get('ingredients', []))
        
        method_options = COOKING_METHODS.copy()
        for ing in input_ingredients:
            if ing in METHOD_PREFERENCES:
                method_options.extend(METHOD_PREFERENCES[ing])
        method = random.choice(method_options) if method_options else "Cook"
        
        prefix = random.choice(FUNNY_PREFIXES)
        suffix = random.choice(FUNNY_SUFFIXES)
        extras = random.sample(SPICES_AND_EXTRAS, k=random.randint(1, 3))
        extra_text = f"Slap on {' and '.join(extras)} for a kick!" if extras else "No extras this time!"
        
        # Use input_ingredients for the ingredients list, even for random recipes
        ingredients_list = sorted(input_ingredients) if input_ingredients else []
        nutrition_items = input_ingredients if input_ingredients else []
        if not ingredients_list and recipe.get('ingredients') and isinstance(recipe['ingredients'], list):
            if recipe['ingredients'] and isinstance(recipe['ingredients'][0], (tuple, list)):
                ingredients_list = sorted([f"{qty} {item}" if qty else item for qty, item in recipe['ingredients']], key=lambda x: x.lower())
                nutrition_items = [item for qty, item in recipe['ingredients']]
            else:
                ingredients_list = sorted([str(item) for item in recipe['ingredients']], key=lambda x: x.lower())
                nutrition_items = [item.split()[-1] for item in recipe['ingredients']]
        recipe['ingredients'] = ingredients_list or ["unknown ingredient"]
        
        title_items = [ing.capitalize() for ing in input_ingredients if ing] if input_ingredients else [item.split()[-1].capitalize() for item in ingredients_list if item]
        if not title_items:
            title_items = ["Mystery"]
        recipe['title'] = f"{prefix} {method} {' and '.join(title_items[:2])} {suffix}"
        
        ingredients_list = ingredients_list or ["unknown"]
        recipe['ingredients_with_links'] = [
            {"name": ing, "url": f"https://www.amazon.com/dp/{AMAZON_ASINS.get(ing.split()[-1], 'B08J4K9L2P')}?tag=bshoemak-20"}
            for ing in ingredients_list
        ]
        recipe['add_all_to_cart'] = f"https://www.amazon.com/gp/aws/cart/add.html?AssociateTag=bshoemak-20&" + "&".join(
            [f"ASIN.{i+1}={AMAZON_ASINS.get(ing.split()[-1], 'B08J4K9L2P')}&Quantity.{i+1}=1" for i, ing in enumerate(ingredients_list)]
        )
        
        equipment = random.sample(EQUIPMENT_OPTIONS, k=min(3, len(EQUIPMENT_OPTIONS))) if EQUIPMENT_OPTIONS else ["pan"]
        if "beer" in input_ingredients and equipment:
            equipment[0] = f"beer-soaked {equipment[0]}"
        if len(equipment) > 1:
            equipment[1] = f"{random.choice(EQUIPMENT_PREFIXES)} {equipment[1]}"
        primary_equipment = equipment[0] if equipment else "pan"
        
        chaos_events = random.sample(CHAOS_EVENTS, k=min(3, len(CHAOS_EVENTS)))
        if "beer" in input_ingredients and chaos_events:
            chaos_events[0] = "Spill half yer beer on yer boots—cook faster!"
        disaster = random.choice(DISASTERS)
        chaos_factor = 10
        insult = f"{random.choice(INSULTS[:2])} {random.choice(INSULTS[2:4])} {random.choice(INSULTS[4:])} {random.choice(INSULTS)}"
        
        steps_key = 'steps_en' if language == 'english' else 'steps_es'
        if steps_key in recipe and recipe[steps_key] and len(recipe[steps_key]) >= 3:
            nonsense = random.choice(NONSENSE) if random.random() < 0.5 else ""
            recipe['steps'] = [
                f"{recipe[steps_key][0]} {extra_text} {method} it in {primary_equipment} ‘til it’s rowdy all at once! {chaos_events[0]} {disaster} {nonsense}",
                f"Serve hot with bread or salad and a holler—garnish if you ain’t too drunk! {chaos_events[1]} {chaos_events[2]} {insult}"
            ]
        else:
            template = random.choice(RECIPE_TEMPLATES)
            nonsense = random.choice(NONSENSE) if random.random() < 0.5 else ""
            recipe['steps'] = [
                template[0].format(ingredients=' and '.join(ingredients_list), method=method.lower(), equipment=primary_equipment, extra=extra_text),
                template[1].format(ingredients=' and '.join(ingredients_list), method=method.lower(), equipment=primary_equipment, extra=extra_text),
                template[2].format(ingredients=' and '.join(ingredients_list), method=method.lower(), equipment=primary_equipment, extra=extra_text) + f" {nonsense} {chaos_events[0]} {disaster} {insult}"
            ]
        recipe['equipment'] = equipment
        
        recipe['steps'].insert(1, f"All yer gear melts—cook with yer boots!")
        if random.random() < 0.5 and equipment:
            risen_gear = random.choice(equipment)
            recipe['steps'].insert(2, random.choice(RESURRECTIONS).format(gear=risen_gear))
        recipe['steps'].append(random.choice(AFTERMATHS))
        recipe['ingredients'] = [f"{ing} (doubled!)" for ing in ingredients_list]
        recipe['steps'].append("Chaos maxed out—double everything and pray!")
        if random.random() < 0.5:
            recipe['steps'].append(random.choice(SINGULARITIES))
        recipe['steps'].append(random.choice(TIME_WARPS))
        
        nutrition_items = nutrition_items or ["unknown"]
        nutrition_future = executor.submit(calculate_nutrition, nutrition_items) if nutrition_items else None
        try:
            nutrition = nutrition_future.result(timeout=5) if nutrition_future else {"calories": random.randint(100, 1000)}
        except TimeoutError:
            logging.warning("Nutrition calculation timed out; using fallback")
            nutrition = {"calories": random.randint(100, 1000)}
        except Exception as e:
            logging.error(f"Nutrition calculation failed: {str(e)}", exc_info=True)
            nutrition = {"calories": random.randint(100, 1000)}
        
        if any(ing in INGREDIENT_CATEGORIES["devil_water"] for ing in nutrition_items):
            nutrition["calories"] += random.randint(100, 666)
        nutrition["calories"] *= 2
        nutrition["chaos_factor"] = chaos_factor
        recipe['nutrition'] = nutrition
        
        recipe['shareText'] = f"Behold my culinary chaos: {recipe['title']}\nGear: {' '.join(equipment)}\nGrub: {' '.join(ingredients_list)}\nSteps:\n{' '.join(recipe['steps'])}\nCalories: {recipe['nutrition']['calories']} (Chaos: {recipe['nutrition']['chaos_factor']}/10)"
        
        for key in ['title_en', 'title_es', 'steps_en', 'steps_es', 'cooking_time', 'difficulty', 'servings', 'tips', 'input_ingredients']:
            recipe.pop(key, None)
        
        return recipe
    except Exception as e:
        logging.error(f"Error processing recipe: {str(e)}", exc_info=True)
        return {"title": "Error Recipe", "ingredients": [], "steps": ["Something went wrong!"], "nutrition": {"calories": 0}}

INGREDIENT_CATEGORIES = {
    "meat": sorted(["ground beef", "chicken", "pork", "lamb", "pichana", "churrasco", "ribeye steaks", "squirrel", "rabbit", "quail", "woodpecker"]),
    "vegetables": sorted(["carrot", "broccoli", "onion", "potato", "tomato", "green beans", "okra", "collards"]),
    "fruits": sorted(["apple", "banana", "lemon", "orange", "mango", "avocado", "starfruit", "dragon fruit", "carambola"]),
    "seafood": sorted(["salmon", "shrimp", "cod", "tuna", "yellowtail snapper", "grouper", "red snapper", "oysters", "lobster", "conch", "lionfish", "catfish", "bass", "crappie"]),
    "dairy": sorted(["cheese", "milk", "butter", "yogurt", "eggs"]),
    "bread_carbs": sorted(["bread", "pasta", "rice", "tortilla"]),
    "devil_water": sorted(["beer", "moonshine", "whiskey", "vodka", "tequila"])
}

@app.route('/', methods=['GET'])
def home():
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
    return jsonify(INGREDIENT_CATEGORIES)

def get_cache_key():
    data = request.get_json(silent=True) or {}
    is_random = data.get('preferences', {}).get('isRandom', False)
    ingredients = sorted(data.get('ingredients', []))
    return f"recipe_{is_random}_{ingredients}"

@app.route('/generate_recipe', methods=['POST', 'OPTIONS'])
@limiter.limit("10 per minute")
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
        
        language = preferences.get('language', 'english').lower()
        is_random = preferences.get('isRandom', False)
        style = preferences.get('style', '')
        category = preferences.get('category', '')
        logging.debug(f"Processing with: language={language}, is_random={is_random}, style={style}, category={category}")

        def process_and_enrich_recipe(recipe):
            logging.debug(f"Processing recipe: {recipe}")
            processed = process_recipe({**recipe, 'input_ingredients': ingredients, 'language': language})
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
            if not ALL_RECIPES:
                logging.warning("ALL_RECIPES is empty; falling back to generate_random_recipe")
                recipe = generate_random_recipe(language)
            else:
                valid_recipes = [r for r in ALL_RECIPES if isinstance(r, dict) and 'ingredients' in r and ('title_en' in r or 'title_es' in r)]
                logging.debug(f"Found {len(valid_recipes)} valid recipes out of {len(ALL_RECIPES)}")
                if not valid_recipes:
                    logging.warning("No valid recipes in ALL_RECIPES; using generate_random_recipe")
                    recipe = generate_random_recipe(language)
                else:
                    scored_recipes = [(r, score_recipe(r, ingredients, preferences)) for r in valid_recipes]
                    top_recipes = sorted(scored_recipes, key=lambda x: x[1], reverse=True)[:5]
                    recipe = random.choice([r for r, _ in top_recipes])
                    logging.debug(f"Selected random recipe from ALL_RECIPES: {recipe}")
            processed_recipe = process_and_enrich_recipe(recipe)
            logging.info(f"Generated random recipe: {processed_recipe.get('title', 'Unknown Recipe')}")
            return jsonify(processed_recipe)

        if ingredients:
            logging.debug("Matching predefined recipe")
            recipe = match_predefined_recipe(ingredients, language)
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

    except ImportError as ie:
        logging.error(f"Import error in generate_recipe: {str(ie)}", exc_info=True)
        return jsonify({"error": "Missing module—check recipe_generator or database imports!"}), 500
    except AttributeError as ae:
        logging.error(f"Attribute error in generate_recipe: {str(ae)}", exc_info=True)
        return jsonify({"error": "Invalid data access—something’s broken in the recipe logic!"}), 500
    except ValueError as ve:
        logging.error(f"Validation error: {str(ve)}", exc_info=True)
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error(f"Unexpected error in generate_recipe: {str(e)}", exc_info=True)
        return jsonify({"error": f"Unexpected error: {str(e)}—check the logs!"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)