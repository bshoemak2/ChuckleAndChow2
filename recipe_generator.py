import random
import logging
from database import get_all_recipes, get_flavor_pairs

logging.basicConfig(level=logging.DEBUG)

def match_predefined_recipe(ingredients, language):
    recipes = get_all_recipes()
    for recipe in recipes:
        if set(ingredients).issubset(set(recipe['ingredients'])):
            title = recipe['title_es'] if language == 'spanish' else recipe['title_en']
            steps = recipe['steps_es'] if language == 'spanish' else recipe['steps_en']
            return {
                "id": recipe['id'],
                "title": title,
                "ingredients": [(ing, "100g") for ing in recipe['ingredients']],
                "steps": steps,
                "nutrition": recipe['nutrition'],
                "cooking_time": recipe['cooking_time'],
                "difficulty": recipe['difficulty'],
                "equipment": recipe.get('equipment', ["skillet"]),
                "servings": recipe.get('servings', 2),
                "tips": recipe.get('tips', "Season to taste!")
            }
    return None

def generate_dynamic_recipe(ingredients, preferences):
    language = preferences.get('language', 'english').lower()
    diet = preferences.get('diet', '').lower()
    time = preferences.get('time', '').lower()
    style = preferences.get('style', '').lower()
    category = preferences.get('category', '').lower()

    if not ingredients:
        title = "No Ingredients" if language == 'english' else "Sin Ingredientes"
        steps = ["Please enter ingredients to generate a recipe!" if language == 'english' else "¡Por favor ingresa ingredientes para generar una receta!"]
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

    main = ingredients[0].lower()
    used_extras = [i.lower() for i in ingredients[1:]] if len(ingredients) > 1 else []

    # Assign realistic quantities
    all_ingredients = [(main, "200g")] + [(extra, "50g") for extra in used_extras]
    title_en = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras]) + ' ' if used_extras else ''}Delight"
    title_es = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras]) + ' ' if used_extras else ''}Delicia"

    # Base cooking times and techniques
    cooking_times = {
        "chicken": 10, "beef": 12, "tofu": 8, "shrimp": 5, "bacon": 6, "egg": 3,
        "rice": 20, "potatoes": 25, "onion": 5, "garlic": 2, "tomatoes": 3
    }
    total_time = cooking_times.get(main, 10) + sum(cooking_times.get(e, 5) for e in used_extras)

    # Detailed steps tailored to ingredients
    steps_en = [
        f"Prep: Trim and cut 200g {main} into bite-sized pieces{' and finely chop ' + ', '.join([f'50g {e}' for e in used_extras]) if used_extras else ''}.",
        f"Heat 2 tbsp {'olive oil' if diet != 'vegan' else 'coconut oil'} in a skillet over medium-high heat."
    ]
    if main in ["rice", "potatoes"]:
        steps_en.append(f"Cook 200g {main} separately: boil in salted water for {cooking_times.get(main, 20)} minutes until tender, then drain.")
    else:
        steps_en.append(f"Add {main} to the skillet and sauté for {cooking_times.get(main, 10)} minutes until cooked through and golden.")

    if used_extras:
        extra_steps = []
        for extra in used_extras:
            if extra in ["rice", "potatoes"]:
                extra_steps.append(f"Cook 50g {extra} separately: boil in salted water for {cooking_times.get(extra, 20)} minutes until tender, then drain.")
            else:
                extra_steps.append(f"Add 50g {extra} and cook for {cooking_times.get(extra, 5)} minutes until tender.")
        steps_en.extend(extra_steps)
        steps_en.append(f"Combine {main} {'and ' + ', '.join([f'50g {e}' for e in used_extras]) if len(used_extras) > 1 else f'and 50g {used_extras[0]}' if used_extras else ''} in the skillet.")
    
    steps_en.extend([
        "Season with 1 tsp salt, 1 tsp ground pepper, and 1/2 tsp of your preferred spice (e.g., paprika).",
        "Serve hot with a side of your choice (e.g., bread or salad). Tip: Garnish with fresh herbs for extra flavor!"
    ])

    steps_es = [
        f"Prepara: Corta 200g de {main} en trozos pequeños{' y pica finamente ' + ', '.join([f'50g de {e}' for e in used_extras]) if used_extras else ''}.",
        f"Calienta 2 cucharadas de {'aceite de oliva' if diet != 'vegan' else 'aceite de coco'} en una sartén a fuego medio-alto."
    ]
    if main in ["rice", "potatoes"]:
        steps_es.append(f"Cocina 200g de {main} por separado: hierve en agua con sal durante {cooking_times.get(main, 20)} minutos hasta que esté tierno, luego escurre.")
    else:
        steps_es.append(f"Añade {main} a la sartén y saltea por {cooking_times.get(main, 10)} minutos hasta que esté cocido y dorado.")

    if used_extras:
        extra_steps = []
        for extra in used_extras:
            if extra in ["rice", "potatoes"]:
                extra_steps.append(f"Cocina 50g de {extra} por separado: hierve en agua con sal durante {cooking_times.get(extra, 20)} minutos hasta que esté tierno, luego escurre.")
            else:
                extra_steps.append(f"Añade 50g de {extra} y cocina por {cooking_times.get(extra, 5)} minutos hasta que esté tierno.")
        steps_es.extend(extra_steps)
        steps_es.append(f"Combina {main} {'y ' + ', '.join([f'50g de {e}' for e in used_extras]) if len(used_extras) > 1 else f'y 50g de {used_extras[0]}' if used_extras else ''} en la sartén.")
    
    steps_es.extend([
        "Sazona con 1 cucharadita de sal, 1 cucharadita de pimienta molida y 1/2 cucharadita de tu especia preferida (p.ej., pimentón).",
        "Sirve caliente con un acompañamiento de tu elección (p.ej., pan o ensalada). ¡Consejo: Decora con hierbas frescas para más sabor!"
    ])

    # Style adjustments
    style_adjustments = {
        "cajun": ("Cajun", "Cajún", "1 tsp Cajun seasoning", "1 tsp paprika, 1/2 tsp cayenne"),
        "latin": ("Latin", "Latino", "1 tsp cumin", "1 tsp chili powder, 1 tbsp chopped cilantro"),
        "asian": ("Asian", "Asiático", "1 tbsp soy sauce", "1 tsp ginger, 1/2 tsp sesame seeds"),
        "mediterranean": ("Mediterranean", "Mediterráneo", "1 tsp oregano", "1 tsp thyme, 1 tbsp olive oil drizzle"),
        "indian": ("Indian", "Indio", "1 tsp cumin seeds", "1 tsp garam masala, 1 tbsp coriander"),
        "french": ("French", "Francés", "1 tsp butter", "1 tsp tarragon, 2 tbsp white wine"),
        "southern": ("Southern", "Sureño", "1 tsp smoked paprika", "1 tsp garlic powder, pinch of cayenne")
    }
    if style in style_adjustments:
        prefix_en, prefix_es, oil_add, season = style_adjustments[style]
        title_en = f"{prefix_en} {title_en}"
        title_es = f"{prefix_es} {title_es}"
        steps_en[1] = f"Heat 2 tbsp {'olive oil' if diet != 'vegan' else 'coconut oil'} in a skillet over medium-high heat and add {oil_add}."
        steps_en[-2] = f"Season with 1 tsp salt, 1 tsp ground pepper, and {season}."
        steps_es[1] = f"Calienta 2 cucharadas de {'aceite de oliva' if diet != 'vegan' else 'aceite de coco'} en una sartén a fuego medio-alto y añade {oil_add}."
        steps_es[-2] = f"Sazona con 1 cucharadita de sal, 1 cucharadita de pimienta molida y {season}."

    # Nutrition based on rough estimates
    nutrition_base = {
        "chicken": {"calories": 165, "protein": 31, "fat": 3.6},
        "rice": {"calories": 130, "protein": 2.7, "fat": 0.3},
        "tofu": {"calories": 76, "protein": 8, "fat": 4.8},
        "bacon": {"calories": 541, "protein": 37, "fat": 42},
        "egg": {"calories": 68, "protein": 6, "fat": 5}
    }
    nutrition = {"calories": 0, "protein": 0, "fat": 0}
    for item, qty in all_ingredients:
        qty_g = int(qty.replace('g', ''))
        base = nutrition_base.get(item, {"calories": 50, "protein": 2, "fat": 2})
        scale = qty_g / 100  # Scale to 100g base
        nutrition["calories"] += base["calories"] * scale
        nutrition["protein"] += base["protein"] * scale
        nutrition["fat"] += base["fat"] * scale

    equipment = ["skillet", "knife", "cutting board"] + (["pot"] if any(i in ["rice", "potatoes"] for i, _ in all_ingredients) else [])
    difficulty = "medium" if len(used_extras) > 1 else "easy"

    return {
        "title": title_es if language == 'spanish' else title_en,
        "ingredients": all_ingredients,
        "steps": steps_es if language == 'spanish' else steps_en,
        "nutrition": nutrition,
        "cooking_time": total_time,
        "difficulty": difficulty,
        "equipment": equipment,
        "servings": 2,
        "tips": "Adjust cooking times based on your stove!"
    }

def generate_random_recipe(language):
    recipes = get_all_recipes()
    if not recipes:
        logging.error("No recipes found in database")
        return {"error": "No recipes available in the database"}
    
    logging.debug(f"Retrieved {len(recipes)} recipes from database")
    random_recipe = random.choice(recipes)
    logging.debug(f"Selected random recipe: {random_recipe}")
    
    title = random_recipe['title_es'] if language == 'spanish' else random_recipe['title_en']
    steps = random_recipe['steps_es'] if language == 'spanish' else random_recipe['steps_en']
    return {
        "id": random_recipe.get('id', 0),
        "title": title,
        "ingredients": [(ing, "100g") for ing in random_recipe.get('ingredients', [])],
        "steps": steps,
        "nutrition": random_recipe.get('nutrition', {"calories": 0, "protein": 0, "fat": 0}),
        "cooking_time": random_recipe.get('cooking_time', 30),
        "difficulty": random_recipe.get('difficulty', 'medium'),
        "equipment": random_recipe.get('equipment', ["skillet"]),
        "servings": random_recipe.get('servings', 2),
        "tips": random_recipe.get('tips', "Season to taste for best results!")
    }