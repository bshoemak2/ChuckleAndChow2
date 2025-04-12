import random
import logging
from database import get_all_recipes, get_flavor_pairs

logging.basicConfig(level=logging.DEBUG)

def match_predefined_recipe(ingredients, language):
    recipes = get_all_recipes()
    for recipe in recipes:
        if set(ingredients).issubset(set(recipe['ingredients'])):
            return {
                "id": recipe['id'],
                "title": recipe['title_en'],
                "ingredients": [(ing, "100g") for ing in recipe['ingredients']],
                "steps": recipe['steps_en'],
                "nutrition": recipe['nutrition'],
                "cooking_time": recipe['cooking_time'],
                "difficulty": recipe['difficulty'],
                "equipment": recipe.get('equipment', ["skillet"]),
                "servings": recipe.get('servings', 2),
                "tips": recipe.get('tips', "Season to taste!")
            }
    return None

def generate_dynamic_recipe(ingredients, preferences):
    diet = preferences.get('diet', '').lower()
    time = preferences.get('time', '').lower()
    style = preferences.get('style', '').lower()
    category = preferences.get('category', '').lower()

    if not ingredients:
        title = "No Ingredients"
        steps = ["Please enter ingredients to generate a recipe!"]
        return {
            "title": title,
            "ingredients": [],
            "steps": steps,
            "nutrition": {"calories": 0, "protein": 0, "fat": 0},
            "cooking_time": 0,
            "difficulty": "N/A",
            "equipment": [],
            "servings": 0,
            "tips": "Add ingredients to start cooking!"
        }

    # Define ingredient categories
    liquid_ingredients = [ing for ing in ingredients if ing in ['beer', 'moonshine', 'whiskey', 'vodka', 'tequila', 'milk']]
    solid_ingredients = [ing for ing in ingredients if ing not in liquid_ingredients]
    main = ingredients[0].lower()
    used_extras = [i.lower() for i in ingredients[1:]] if len(ingredients) > 1 else []

    # Assign realistic quantities
    meat_ingredients = ['ground beef', 'chicken', 'pork', 'shrimp', 'ribeye steaks', 'lamb', 'pichana', 'churrasco', 'squirrel', 'rabbit', 'quail', 'woodpecker']
    dairy_ingredients = ['cheese', 'butter', 'yogurt', 'eggs']
    all_ingredients = [(main, "1 lb" if main in meat_ingredients else "2 tbsp" if main in dairy_ingredients else "1/2 cup" if main in liquid_ingredients else "1 cup")]
    all_ingredients += [(extra, "1/2 cup" if extra in liquid_ingredients else "1 lb" if extra in meat_ingredients else "2 tbsp" if extra in dairy_ingredients else "1 cup") for extra in used_extras]
    
    title = f"{main.capitalize()} {' and '.join([e.capitalize() for e in used_extras]) + ' ' if used_extras else ''}Delight"

    # Base cooking times and techniques
    cooking_times = {
        "chicken": 10, "ground beef": 12, "tofu": 8, "shrimp": 5, "bacon": 6, "egg": 3,
        "rice": 20, "potato": 25, "onion": 5, "garlic": 2, "tomato": 3,
        "beer": 5, "moonshine": 5, "whiskey": 5, "vodka": 5, "tequila": 5, "milk": 5,
        "ribeye steaks": 10, "squirrel": 10, "rabbit": 10, "quail": 8, "woodpecker": 10,
        "butter": 2, "cheese": 2, "yogurt": 2, "eggs": 3
    }
    total_time = cooking_times.get(main, 10) + sum(cooking_times.get(e, 5) for e in used_extras)

    # Generate steps tailored to ingredients
    steps = []
    if solid_ingredients:
        steps.append(f"Prep: Chop {', '.join(solid_ingredients)} into bite-sized pieces—mind yer fingers!")
    if liquid_ingredients:
        steps.append(f"Measure out {', '.join([f'1/2 cup {ing}' for ing in liquid_ingredients])}—don’t drink it yet!")
    
    oil = 'olive oil' if diet != 'vegan' else 'coconut oil'
    steps.append(f"Heat 2 tbsp {oil} in a skillet over medium-high heat.")
    
    if main in ["rice", "potato"]:
        steps.append(f"Cook {all_ingredients[0][1]} {main} separately: boil in salted water for {cooking_times.get(main, 20)} minutes until tender, then drain.")
    else:
        steps.append(f"Add {all_ingredients[0][1]} {main} to the skillet and sauté for {cooking_times.get(main, 10)} minutes until cooked through.")

    if used_extras:
        for extra, qty in all_ingredients[1:]:
            if extra in ["rice", "potato"]:
                steps.append(f"Cook {qty} {extra} separately: boil in salted water for {cooking_times.get(extra, 20)} minutes until tender, then drain.")
            elif extra in liquid_ingredients:
                steps.append(f"Pour in {qty} {extra} and simmer for {cooking_times.get(extra, 5)} minutes to blend flavors.")
            else:
                steps.append(f"Add {qty} {extra} and cook for {cooking_times.get(extra, 5)} minutes until tender.")
    
    steps.extend([
        "Season with 1 tsp salt, 1 tsp pepper, and a pinch of paprika—give it some sass!",
        "Serve hot with cornbread or a side salad. Yeehaw!"
    ])

    # Nutrition estimates
    nutrition_base = {
        "chicken": {"calories": 165, "protein": 31, "fat": 3.6},
        "ground beef": {"calories": 250, "protein": 26, "fat": 15},
        "tofu": {"calories": 76, "protein": 8, "fat": 4.8},
        "bacon": {"calories": 541, "protein": 37, "fat": 42},
        "egg": {"calories": 68, "protein": 6, "fat": 5},
        "rice": {"calories": 130, "protein": 2.7, "fat": 0.3},
        "potato": {"calories": 77, "protein": 2, "fat": 0.1},
        "beer": {"calories": 43, "protein": 0.5, "fat": 0},
        "ribeye steaks": {"calories": 271, "protein": 25, "fat": 19},
        "squirrel": {"calories": 170, "protein": 30, "fat": 5},
        "rabbit": {"calories": 173, "protein": 33, "fat": 3.5},
        "quail": {"calories": 192, "protein": 25, "fat": 10},
        "woodpecker": {"calories": 180, "protein": 28, "fat": 7},
        "butter": {"calories": 717, "protein": 0.9, "fat": 81}
    }
    nutrition = {"calories": 0, "protein": 0, "fat": 0}
    for item, qty in all_ingredients:
        qty_parts = qty.split()
        qty_str = qty_parts[0]
        unit = qty_parts[1] if len(qty_parts) > 1 else 'cup'
        try:
            if '/' in qty_str:
                num, denom = qty_str.split('/')
                qty_num = float(num) / float(denom)
            else:
                qty_num = float(qty_str)
        except ValueError:
            qty_num = 1.0
        if unit == 'lb':
            qty_g = qty_num * 453.6
        elif unit == 'tbsp':
            qty_g = qty_num * 15
        elif unit == 'cup':
            qty_g = qty_num * 240
        else:
            qty_g = qty_num * 100
        base = nutrition_base.get(item, {"calories": 50, "protein": 2, "fat": 2})
        scale = qty_g / 100
        nutrition["calories"] += base["calories"] * scale
        nutrition["protein"] += base["protein"] * scale
        nutrition["fat"] += base["fat"] * scale

    equipment = ["skillet", "knife", "cutting board"] + (["pot"] if any(i in ["rice", "potato"] for i, _ in all_ingredients) else [])
    difficulty = "medium" if len(used_extras) > 1 else "easy"

    return {
        "title": title,
        "ingredients": all_ingredients,
        "steps": steps,
        "nutrition": nutrition,
        "cooking_time": total_time,
        "difficulty": difficulty,
        "equipment": equipment,
        "servings": 2,
        "tips": "Adjust cooking times based on your stove!",
        "input_ingredients": ingredients
    }

def generate_random_recipe(language):
    recipes = get_all_recipes()
    if not recipes:
        logging.error("No recipes found in database")
        return {"error": "No recipes available in the database"}
    
    logging.debug(f"Retrieved {len(recipes)} recipes from database")
    random_recipe = random.choice(recipes)
    logging.debug(f"Selected random recipe: {random_recipe}")
    
    return {
        "id": random_recipe.get('id', 0),
        "title": random_recipe['title_en'],
        "ingredients": [(ing, "100g") for ing in random_recipe.get('ingredients', [])],
        "steps": random_recipe['steps_en'],
        "nutrition": random_recipe.get('nutrition', {"calories": 0, "protein": 0, "fat": 0}),
        "cooking_time": random_recipe.get('cooking_time', 30),
        "difficulty": random_recipe.get('difficulty', 'medium'),
        "equipment": random_recipe.get('equipment', ["skillet"]),
        "servings": random_recipe.get('servings', 2),
        "tips": random_recipe.get('tips', "Season to taste for best results!")
    }