from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random

app = Flask(__name__)

# Rate limiting: 100 requests/day, 10/minute per IP
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day", "10 per minute"])

# Expanded list of random recipes (unchanged from your latest version)
RANDOM_RECIPES = [
    {
        "title_en": "Ginger-Soy Tofu Stir-Fry",
        "title_es": "Tofu Salteado con Jengibre y Salsa de Soja",
        "steps_en": [
            "Heat sesame oil in a pan over medium heat.",
            "Add diced tofu and fry until golden, about 5 minutes.",
            "Stir in grated ginger and soy sauce, cook for 2 minutes.",
            "Add any additional veggies and stir-fry for 3 minutes.",
            "Serve over rice with a sprinkle of sesame seeds."
        ],
        "steps_es": [
            "Calienta aceite de sésamo en una sartén a fuego medio.",
            "Añade tofu en cubos y fríe hasta que esté dorado, unos 5 minutos.",
            "Incorpora jengibre rallado y salsa de soja, cocina por 2 minutos.",
            "Añade otras verduras y saltea por 3 minutos.",
            "Sirve sobre arroz con un toque de semillas de sésamo."
        ],
        "nutrition": {"calories": 320, "protein": 18, "fat": 12},
        "ingredients": ["tofu", "ginger", "soy sauce"]
    },
    {
        "title_en": "Creamy Coconut Chicken Curry",
        "title_es": "Curry Cremoso de Pollo con Leche de Coco",
        "steps_en": [
            "Heat oil in a pan over medium heat.",
            "Sauté chicken pieces until browned, about 5 minutes.",
            "Add curry powder and stir for 1 minute to toast the spices.",
            "Pour in coconut milk, simmer for 15 minutes until chicken is tender.",
            "Serve with rice or naan, garnished with fresh cilantro."
        ],
        "steps_es": [
            "Calienta aceite en una sartén a fuego medio.",
            "Saltea trozos de pollo hasta que estén dorados, unos 5 minutos.",
            "Añade polvo de curry y revuelve por 1 minuto para tostar las especias.",
            "Vierte la leche de coco, cocina a fuego lento por 15 minutos hasta que el pollo esté tierno.",
            "Sirve con arroz o naan, decorado con cilantro fresco."
        ],
        "nutrition": {"calories": 450, "protein": 30, "fat": 20},
        "ingredients": ["chicken", "curry", "coconut milk"]
    },
    {
        "title_en": "Classic Hummus",
        "title_es": "Hummus Clásico",
        "steps_en": [
            "Drain and rinse chickpeas, then add to a food processor.",
            "Add tahini, lemon juice, garlic, and a pinch of salt.",
            "Blend until smooth, adding water as needed to reach desired consistency.",
            "Drizzle with olive oil and sprinkle with paprika before serving.",
            "Serve with pita bread or fresh veggies."
        ],
        "steps_es": [
            "Escurre y enjuaga los garbanzos, luego añádelos a un procesador de alimentos.",
            "Agrega tahini, jugo de limón, ajo y una pizca de sal.",
            "Mezcla hasta que esté suave, añadiendo agua según sea necesario para la consistencia deseada.",
            "Rocía con aceite de oliva y espolvorea con pimentón antes de servir.",
            "Sirve con pan pita o verduras frescas."
        ],
        "nutrition": {"calories": 200, "protein": 8, "fat": 10},
        "ingredients": ["chickpeas", "tahini", "lemon"]
    },
    {
        "title_en": "Southern Cheesy Cauliflower Bake",
        "title_es": "Gratinado de Coliflor con Queso al Estilo Sureño",
        "steps_en": [
            "Preheat oven to 375°F (190°C).",
            "Steam cauliflower florets until tender, about 5 minutes.",
            "In a skillet, cook bacon until crispy, then crumble and set aside.",
            "Mix steamed cauliflower with diced ham, shredded cheese, and crumbled bacon in a baking dish.",
            "Bake for 20 minutes until the cheese is melted and bubbly, then serve hot."
        ],
        "steps_es": [
            "Precalienta el horno a 190°C.",
            "Cocina al vapor los floretes de coliflor hasta que estén tiernos, unos 5 minutos.",
            "En una sartén, cocina el tocino hasta que esté crujiente, luego desmenúzalo y reserva.",
            "Mezcla la coliflor al vapor con jamón en cubos, queso rallado y tocino desmenuzado en un molde para hornear.",
            "Hornea durante 20 minutos hasta que el queso esté derretido y burbujeante, luego sirve caliente."
        ],
        "nutrition": {"calories": 380, "protein": 22, "fat": 28},
        "ingredients": ["cauliflower", "ham", "cheese", "bacon"]
    },
    {
        "title_en": "Southern Black-Eyed Peas and Greens",
        "title_es": "Guisantes de Ojo Negro y Verduras al Estilo Sureño",
        "steps_en": [
            "In a large pot, cook diced ham with a bit of oil until browned, about 5 minutes.",
            "Add chopped collard greens and cook until wilted, about 3 minutes.",
            "Stir in black-eyed peas, a pinch of smoked paprika, and a splash of broth.",
            "Simmer for 15 minutes until flavors meld together.",
            "Serve hot with cornbread on the side."
        ],
        "steps_es": [
            "En una olla grande, cocina el jamón en cubos con un poco de aceite hasta que esté dorado, unos 5 minutos.",
            "Añade las acelgas picadas y cocina hasta que se marchiten, unos 3 minutos.",
            "Incorpora los guisantes de ojo negro, una pizca de pimentón ahumado y un chorrito de caldo.",
            "Cocina a fuego lento durante 15 minutos hasta que los sabores se mezclen.",
            "Sirve caliente con pan de maíz al lado."
        ],
        "nutrition": {"calories": 300, "protein": 18, "fat": 10},
        "ingredients": ["black-eyed peas", "ham", "collard greens"]
    },
    {
        "title_en": "Spicy Shrimp Tacos",
        "title_es": "Tacos de Camarones Picantes",
        "steps_en": [
            "Toss shrimp with chili powder, cumin, and a pinch of salt.",
            "Heat oil in a skillet over medium-high heat.",
            "Cook shrimp until pink and opaque, about 2-3 minutes per side.",
            "Warm tortillas and fill with shrimp, diced tomatoes, and cilantro.",
            "Serve with lime wedges and a dollop of sour cream."
        ],
        "steps_es": [
            "Mezcla los camarones con chile en polvo, comino y una pizca de sal.",
            "Calienta aceite en una sartén a fuego medio-alto.",
            "Cocina los camarones hasta que estén rosados y opacos, unos 2-3 minutos por lado.",
            "Calienta tortillas y rellénalas con camarones, tomates en cubos y cilantro.",
            "Sirve con gajos de limón y una cucharada de crema agria."
        ],
        "nutrition": {"calories": 350, "protein": 25, "fat": 15},
        "ingredients": ["shrimp", "chili", "tomatoes", "cilantro"]
    },
    {
        "title_en": "Blueberry Oat Muffins",
        "title_es": "Muffins de Avena y Arándanos",
        "steps_en": [
            "Preheat oven to 375°F (190°C) and line a muffin tin.",
            "Mix oats, flour, sugar, baking powder, and a pinch of salt in a bowl.",
            "Stir in blueberries, then add milk, egg, and melted butter.",
            "Fill muffin cups 3/4 full and bake for 20-25 minutes until golden.",
            "Cool slightly and enjoy warm or store for later."
        ],
        "steps_es": [
            "Precalienta el horno a 190°C y forra un molde para muffins.",
            "Mezcla avena, harina, azúcar, polvo de hornear y una pizca de sal en un tazón.",
            "Incorpora los arándanos, luego añade leche, huevo y mantequilla derretida.",
            "Llena los moldes para muffins 3/4 y hornea por 20-25 minutos hasta que estén dorados.",
            "Enfría un poco y disfruta tibios o guárdalos para después."
        ],
        "nutrition": {"calories": 180, "protein": 4, "fat": 6},
        "ingredients": ["oats", "blueberries", "milk", "egg"]
    },
    {
        "title_en": "Roasted Pumpkin Soup",
        "title_es": "Sopa de Calabaza Asada",
        "steps_en": [
            "Preheat oven to 400°F (200°C).",
            "Cut pumpkin in half, scoop out seeds, and roast cut-side down for 40 minutes.",
            "Scoop out flesh and blend with broth, garlic, and a pinch of nutmeg.",
            "Simmer on stovetop for 10 minutes, stirring occasionally.",
            "Serve hot with a swirl of cream and toasted pumpkin seeds."
        ],
        "steps_es": [
            "Precalienta el horno a 200°C.",
            "Corta la calabaza por la mitad, retira las semillas y asa con el lado cortado hacia abajo por 40 minutos.",
            "Saca la pulpa y mezcla con caldo, ajo y una pizca de nuez moscada.",
            "Cocina a fuego lento en la estufa por 10 minutos, revolviendo ocasionalmente.",
            "Sirve caliente con un toque de crema y semillas de calabaza tostadas."
        ],
        "nutrition": {"calories": 250, "protein": 5, "fat": 8},
        "ingredients": ["pumpkin", "garlic", "nutmeg"]
    },
    {
        "title_en": "Mango Avocado Salsa Chicken",
        "title_es": "Pollo con Salsa de Mango y Aguacate",
        "steps_en": [
            "Grill chicken breasts until cooked through, about 6-8 minutes per side.",
            "Dice mango and avocado, mix with lime juice, cilantro, and a pinch of salt.",
            "Spoon salsa over grilled chicken.",
            "Serve with rice or a side salad."
        ],
        "steps_es": [
            "Asa pechugas de pollo hasta que estén cocidas, unos 6-8 minutos por lado.",
            "Corta mango y aguacate en cubos, mezcla con jugo de lima, cilantro y una pizca de sal.",
            "Coloca la salsa sobre el pollo asado.",
            "Sirve con arroz o una ensalada."
        ],
        "nutrition": {"calories": 400, "protein": 35, "fat": 15},
        "ingredients": ["chicken", "mango", "avocado", "lime"]
    },
    {
        "title_en": "Beet and Goat Cheese Salad",
        "title_es": "Ensalada de Remolacha y Queso de Cabra",
        "steps_en": [
            "Roast beets at 400°F (200°C) wrapped in foil for 45 minutes, then peel and dice.",
            "Toss arugula with olive oil and balsamic vinegar.",
            "Top with diced beets, crumbled goat cheese, and walnuts.",
            "Season with salt and pepper, serve fresh."
        ],
        "steps_es": [
            "Asa remolachas a 200°C envueltas en papel aluminio por 45 minutos, luego pélalas y córtalas en cubos.",
            "Mezcla rúcula con aceite de oliva y vinagre balsámico.",
            "Añade remolachas en cubos, queso de cabra desmenuzado y nueces.",
            "Sazona con sal y pimienta, sirve fresco."
        ],
        "nutrition": {"calories": 280, "protein": 10, "fat": 20},
        "ingredients": ["beets", "goat cheese", "arugula", "walnuts"]
    },
    {
        "title_en": "Squid Ink Pasta with Shrimp",
        "title_es": "Pasta de Tinta de Calamar con Camarones",
        "steps_en": [
            "Cook squid ink pasta in salted boiling water until al dente, about 8-10 minutes.",
            "Sauté shrimp with garlic and olive oil until pink, about 3 minutes per side.",
            "Toss pasta with shrimp, a squeeze of lemon, and red pepper flakes.",
            "Serve with a sprinkle of parsley."
        ],
        "steps_es": [
            "Cocina pasta de tinta de calamar en agua hirviendo con sal hasta que esté al dente, unos 8-10 minutos.",
            "Saltea camarones con ajo y aceite de oliva hasta que estén rosados, unos 3 minutos por lado.",
            "Mezcla la pasta con camarones, un chorrito de limón y hojuelas de pimiento rojo.",
            "Sirve con un toque de perejil."
        ],
        "nutrition": {"calories": 420, "protein": 25, "fat": 12},
        "ingredients": ["squid", "pasta", "shrimp", "garlic"]
    },
    {
        "title_en": "Cherry Almond Crisp",
        "title_es": "Crujiente de Cereza y Almendra",
        "steps_en": [
            "Preheat oven to 375°F (190°C).",
            "Mix pitted cherries with sugar and a splash of lemon juice in a baking dish.",
            "In a bowl, combine oats, flour, brown sugar, and chopped almonds with melted butter.",
            "Spread topping over cherries and bake for 30 minutes until golden and bubbly.",
            "Serve warm with a scoop of vanilla ice cream."
        ],
        "steps_es": [
            "Precalienta el horno a 190°C.",
            "Mezcla cerezas deshuesadas con azúcar y un chorrito de jugo de limón en un molde para hornear.",
            "En un tazón, combina avena, harina, azúcar moreno y almendras picadas con mantequilla derretida.",
            "Extiende la cobertura sobre las cerezas y hornea por 30 minutos hasta que esté dorado y burbujeante.",
            "Sirve tibio con una bola de helado de vainilla."
        ],
        "nutrition": {"calories": 320, "protein": 6, "fat": 14},
        "ingredients": ["cherries", "almonds", "oats", "brown sugar"]
    },
    {
        "title_en": "Pork and Apple Skillet",
        "title_es": "Sartén de Cerdo y Manzana",
        "steps_en": [
            "Heat oil in a skillet over medium heat.",
            "Season pork chops with salt, pepper, and thyme, then cook until browned, about 5 minutes per side.",
            "Add sliced apples and a splash of apple cider vinegar, cook for 5 more minutes.",
            "Serve hot with mashed potatoes or a green salad."
        ],
        "steps_es": [
            "Calienta aceite en una sartén a fuego medio.",
            "Sazona chuletas de cerdo con sal, pimienta y tomillo, luego cocina hasta que estén doradas, unos 5 minutos por lado.",
            "Añade manzanas en rodajas y un chorrito de vinagre de sidra de manzana, cocina por 5 minutos más.",
            "Sirve caliente con puré de papas o una ensalada verde."
        ],
        "nutrition": {"calories": 450, "protein": 35, "fat": 20},
        "ingredients": ["pork", "apple", "thyme"]
    },
    {
        "title_en": "Couscous Stuffed Peppers",
        "title_es": "Pimientos Rellenos de Cuscús",
        "steps_en": [
            "Preheat oven to 375°F (190°C).",
            "Cook couscous in broth according to package instructions.",
            "Mix cooked couscous with diced tomatoes, feta, and chopped parsley.",
            "Cut tops off bell peppers, remove seeds, and stuff with couscous mixture.",
            "Bake for 25-30 minutes until peppers are tender, then serve warm."
        ],
        "steps_es": [
            "Precalienta el horno a 190°C.",
            "Cocina el cuscús en caldo según las instrucciones del paquete.",
            "Mezcla el cuscús cocido con tomates en cubos, feta y perejil picado.",
            "Corta la parte superior de los pimientos, quita las semillas y rellénalos con la mezcla de cuscús.",
            "Hornea por 25-30 minutos hasta que los pimientos estén tiernos, luego sirve tibio."
        ],
        "nutrition": {"calories": 300, "protein": 10, "fat": 12},
        "ingredients": ["couscous", "tomatoes", "feta", "pepper"]
    },
    {
        "title_en": "Raspberry Chia Pudding",
        "title_es": "Pudín de Chía y Frambuesas",
        "steps_en": [
            "Mix chia seeds with milk and a drizzle of honey in a bowl.",
            "Let sit in the fridge for at least 4 hours or overnight until thickened.",
            "Top with fresh raspberries and a sprinkle of coconut flakes before serving.",
            "Enjoy chilled as a healthy breakfast or dessert."
        ],
        "steps_es": [
            "Mezcla semillas de chía con leche y un chorrito de miel en un tazón.",
            "Deja reposar en el refrigerador por al menos 4 horas o toda la noche hasta que espese.",
            "Cubre con frambuesas frescas y un poco de coco rallado antes de servir.",
            "Disfruta frío como un desayuno o postre saludable."
        ],
        "nutrition": {"calories": 220, "protein": 6, "fat": 10},
        "ingredients": ["chia seeds", "milk", "raspberries", "honey"]
    }
]

# Expanded flavor pairing dictionary
FLAVOR_PAIRS = {
    "chicken": ["curry", "coconut milk", "garlic", "ginger", "lemon", "rosemary", "thyme", "lime", "mango", "avocado"],
    "tofu": ["soy sauce", "ginger", "garlic", "sesame oil", "chili", "peanuts"],
    "beef": ["mushrooms", "thyme", "garlic", "rosemary", "paprika", "red wine"],
    "shrimp": ["garlic", "capers", "lemon", "chili", "cilantro", "lime", "pasta", "squid"],
    "lamb": ["rosemary", "garlic", "thyme", "mint", "red wine"],
    "pasta": ["tomatoes", "basil", "parmesan", "olive oil", "garlic", "squid", "shrimp"],
    "salmon": ["lemon", "dill", "garlic", "capers", "mustard"],
    "cauliflower": ["cheese", "bacon", "ham", "paprika", "curry"],
    "black-eyed peas": ["ham", "collard greens", "paprika", "onion"],
    "arugula": ["parmesan", "lemon", "olive oil", "goat cheese", "beets", "walnuts"],
    "butternut squash": ["sage", "honey", "nutmeg", "cinnamon"],
    "chickpeas": ["tahini", "lemon", "garlic", "cumin", "paprika"],
    "oats": ["blueberries", "milk", "honey", "cinnamon", "banana", "almonds"],
    "pumpkin": ["nutmeg", "garlic", "cream", "sage"],
    "mango": ["lime", "cilantro", "chicken", "avocado", "chili"],
    "beets": ["goat cheese", "arugula", "walnuts", "balsamic vinegar"],
    "squid": ["pasta", "shrimp", "garlic", "lemon", "red pepper flakes"],
    "pork": ["garlic", "thyme", "rosemary", "apple", "mustard", "honey"],
    "fish": ["lemon", "dill", "garlic", "olive oil", "capers"],
    "egg": ["spinach", "feta", "cheese", "tomatoes", "onion"],
    "avocado": ["lime", "cilantro", "tomatoes", "chicken", "mango"],
    "blueberries": ["oats", "honey", "milk", "yogurt", "almonds"],
    "cherries": ["almonds", "oats", "brown sugar", "vanilla"],
    "couscous": ["tomatoes", "feta", "parsley", "pepper", "lemon"],
    "chia seeds": ["milk", "raspberries", "honey", "coconut"]
}

@app.route('/generate_recipe', methods=['POST'])
@limiter.limit("10 per minute")  # Specific rate limit for this endpoint
def generate_recipe():
    # Input validation
    data = request.json
    if not isinstance(data, dict) or 'ingredients' not in data:
        abort(400, "Invalid request: 'ingredients' required")
    ingredients = data.get('ingredients', [])
    if not isinstance(ingredients, list) or len(ingredients) > 10:
        abort(400, "Invalid ingredients: must be a list with max 10 items")
    ingredients = [str(i)[:50].strip() for i in ingredients if isinstance(i, str)]  # Sanitize: max 50 chars, strip whitespace
    
    preferences = data.get('preferences', {})
    if not isinstance(preferences, dict):
        abort(400, "Invalid preferences: must be a dictionary")
    
    diet = preferences.get('diet', '').lower()
    time = preferences.get('time', '').lower()
    language = preferences.get('language', 'english').lower()
    style = preferences.get('style', '').lower()
    category = preferences.get('category', '').lower()
    is_random = preferences.get('isRandom', False)

    # Random recipe from predefined list
    if is_random:
        random_recipe = random.choice(RANDOM_RECIPES)
        title = random_recipe['title_es'] if language == 'spanish' else random_recipe['title_en']
        steps = random_recipe['steps_es'] if language == 'spanish' else random_recipe['steps_en']
        share_text_en = f"Check out my recipe: {random_recipe['title_en']}\nIngredients: {', '.join(random_recipe['ingredients'])}\nSteps:\n" + \
                        "\n".join([f"{i+1}. {step}" for i, step in enumerate(random_recipe['steps_en'])]) + \
                        f"\nNutrition: {random_recipe['nutrition']['calories']} kcal, {random_recipe['nutrition']['protein']}g protein"
        share_text_es = f"Mira mi receta: {random_recipe['title_es']}\nIngredientes: {', '.join(random_recipe['ingredients'])}\nPasos:\n" + \
                        "\n".join([f"{i+1}. {step}" for i, step in enumerate(random_recipe['steps_es'])]) + \
                        f"\nNutrición: {random_recipe['nutrition']['calories']} kcal, {random_recipe['nutrition']['protein']}g proteína"
        return jsonify({
            "title": title,
            "ingredients": random_recipe['ingredients'],
            "steps": steps,
            "nutrition": random_recipe['nutrition'],
            "shareText": share_text_es if language == 'spanish' else share_text_en
        })

    # Check predefined recipes with subset matching
    if ingredients:
        for r in RANDOM_RECIPES:
            if set(ingredients).issubset(set(r['ingredients'])):
                title = r['title_es'] if language == 'spanish' else r['title_en']
                steps = r['steps_es'] if language == 'spanish' else r['steps_en']
                share_text_en = f"Check out my recipe: {r['title_en']}\nIngredients: {', '.join(ingredients)}\nSteps:\n" + \
                                "\n".join([f"{i+1}. {step}" for i, step in enumerate(r['steps_en'])]) + \
                                f"\nNutrition: {r['nutrition']['calories']} kcal, {r['nutrition']['protein']}g protein"
                share_text_es = f"Mira mi receta: {r['title_es']}\nIngredientes: {', '.join(ingredients)}\nPasos:\n" + \
                                "\n".join([f"{i+1}. {step}" for i, step in enumerate(r['steps_es'])]) + \
                                f"\nNutrición: {r['nutrition']['calories']} kcal, {r['nutrition']['protein']}g proteína"
                return jsonify({
                    "title": title,
                    "ingredients": ingredients,
                    "steps": steps,
                    "nutrition": r['nutrition'],
                    "shareText": share_text_es if language == 'spanish' else share_text_en
                })

    # Dynamic recipe generation with flavor pairing
    if not ingredients:
        if language == 'spanish':
            return jsonify({
                "title": "Delicia Sorpresa",
                "steps": ["Calienta aceite en una sartén.", "Añade una proteína o verdura de tu elección.", "Cocina por 5-7 minutos.", "Sazona y sirve!"],
                "nutrition": {"calories": 250, "protein": 5, "fat": 5},
                "ingredients": ["¡Tu elección!"],
                "shareText": "Mira mi receta: Delicia Sorpresa\nIngredientes: ¡Tu elección!\nPasos:\n1. Calienta aceite en una sartén.\n2. Añade una proteína o verdura de tu elección.\n3. Cocina por 5-7 minutos.\n4. Sazona y sirve!\nNutrición: 250 kcal, 5g proteína"
            })
        return jsonify({
            "title": "Surprise Delight",
            "steps": ["Heat oil in a skillet.", "Add a protein or veggie of your choice.", "Cook for 5-7 minutes.", "Season and serve!"],
            "nutrition": {"calories": 250, "protein": 5, "fat": 5},
            "ingredients": ["Your choice!"],
            "shareText": "Check out my recipe: Surprise Delight\nIngredients: Your choice!\nSteps:\n1. Heat oil in a skillet.\n2. Add a protein or veggie of your choice.\n3. Cook for 5-7 minutes.\n4. Season and serve!\nNutrition: 250 kcal, 5g protein"
        })

    main = ingredients[0].lower() if ingredients else "surprise"
    extras = [i.lower() for i in ingredients[1:]] if len(ingredients) > 1 else []
    paired_extras = FLAVOR_PAIRS.get(main, []) if main in FLAVOR_PAIRS else ["surprise"]
    used_extras = [e for e in extras if e in paired_extras] or random.sample(paired_extras, min(len(paired_extras), 2)) if paired_extras else ["surprise"]
    all_ingredients = [main] + used_extras

    title_en = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras])} Delight"
    title_es = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras])} Delicia"
    steps_en = [
        f"Heat oil in a skillet over medium heat.",
        f"Add {main} and cook until ready, about 5-7 minutes.",
        f"Stir in {', '.join(used_extras)} and cook for another 5 minutes.",
        "Season with salt, pepper, and your favorite spices.",
        "Serve hot and enjoy!"
    ]
    steps_es = [
        f"Calienta aceite en una sartén a fuego medio.",
        f"Añade {main} y cocina hasta que esté listo, unos 5-7 minutos.",
        f"Incorpora {', '.join(used_extras)} y cocina por otros 5 minutos.",
        "Sazona con sal, pimienta y tus especias favoritas.",
        "¡Sirve caliente y disfruta!"
    ]

    # Style adjustments
    if style == "cajun":
        title_en = f"Cajun {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Cajún {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat oil in a skillet and add Cajun seasoning."
        steps_en[3] = "Season with Cajun spices, paprika, and a pinch of cayenne."
        steps_es[0] = "Calienta aceite en una sartén y añade condimento cajún."
        steps_es[3] = "Sazona con especias cajún, pimentón y una pizca de cayena."
    elif style == "latin":
        title_en = f"Latin {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Latino {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat oil in a skillet with a splash of lime."
        steps_en[3] = "Season with cumin, cilantro, and chili powder."
        steps_es[0] = "Calienta aceite en una sartén con un toque de lima."
        steps_es[3] = "Sazona con comino, cilantro y chile en polvo."
    elif style == "asian":
        title_en = f"Asian {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Asiático {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat sesame oil in a wok over high heat."
        steps_en[3] = "Season with soy sauce, ginger, and sesame seeds."
        steps_es[0] = "Calienta aceite de sésamo en un wok a fuego alto."
        steps_es[3] = "Sazona con salsa de soja, jengibre y semillas de sésamo."
    elif style == "mediterranean":
        title_en = f"Mediterranean {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Mediterráneo {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat olive oil in a skillet over medium heat."
        steps_en[3] = "Season with oregano, thyme, and a drizzle of olive oil."
        steps_es[0] = "Calienta aceite de oliva en una sartén a fuego medio."
        steps_es[3] = "Sazona con orégano, tomillo y un chorrito de aceite de oliva."
    elif style == "indian":
        title_en = f"Indian {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Indio {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat oil in a pan and add cumin seeds until they sizzle."
        steps_en[3] = "Season with turmeric, garam masala, and coriander."
        steps_es[0] = "Calienta aceite en una sartén y añade semillas de comino hasta que chisporroteen."
        steps_es[3] = "Sazona con cúrcuma, garam masala y cilantro."
    elif style == "french":
        title_en = f"French {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Francés {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat butter in a skillet over medium heat."
        steps_en[3] = "Season with tarragon, thyme, and a splash of white wine."
        steps_es[0] = "Calienta mantequilla en una sartén a fuego medio."
        steps_es[3] = "Sazona con estragón, tomillo y un chorrito de vino blanco."
    elif style == "southern":
        title_en = f"Southern {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        title_es = f"Sureño {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[0] = "Heat oil in a skillet with a touch of butter for that Southern flair."
        steps_en[3] = "Season with smoked paprika, garlic powder, and a pinch of cayenne for a Southern kick."
        steps_es[0] = "Calienta aceite en una sartén con un toque de mantequilla para ese toque sureño."
        steps_es[3] = "Sazona con pimentón ahumado, ajo en polvo y una pizca de cayena para un toque sureño."

    # Category adjustments
    if category == "dinner":
        steps_en[-1] = "Serve hot with a side of your choice and enjoy!"
        steps_es[-1] = "¡Sirve caliente con un acompañamiento de tu elección y disfruta!"
    elif category == "dessert":
        title_en = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras])} Dessert"
        title_es = f"Postre de {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en = [
            f"Preheat oven to 350°F (175°C).",
            f"Mix {main} with sugar and butter.",
            f"Add {', '.join(used_extras)} and blend well.",
            "Bake for 20-25 minutes until golden.",
            "Cool slightly and serve with a sweet topping!"
        ]
        steps_es = [
            f"Precalienta el horno a 175°C.",
            f"Mezcla {main} con azúcar y mantequilla.",
            f"Añade {', '.join(used_extras)} y mezcla bien.",
            "Hornea por 20-25 minutos hasta que esté dorado.",
            "¡Enfría un poco y sirve con un topping dulce!"
        ]
    elif category == "breakfast":
        title_en = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras])} Breakfast"
        title_es = f"Desayuno de {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en = [
            f"Heat a non-stick skillet over medium heat.",
            f"Add {main} and cook until ready, about 5 minutes.",
            f"Mix in {', '.join(used_extras)} and cook for another 2 minutes.",
            "Serve with toast or a side of fruit.",
            "Enjoy your hearty breakfast!"
        ]
        steps_es = [
            f"Calienta una sartén antiadherente a fuego medio.",
            f"Añade {main} y cocina hasta que esté listo, unos 5 minutos.",
            f"Incorpora {', '.join(used_extras)} y cocina por otros 2 minutos.",
            "Sirve con tostadas o una guarnición de fruta.",
            "¡Disfruta de tu desayuno sustancioso!"
        ]
    elif category == "lunch":
        title_en = f"{main.capitalize()} {' '.join([e.capitalize() for e in used_extras])} Lunch"
        title_es = f"Almuerzo de {main.capitalize()} {' '.join([e.capitalize() for e in used_extras])}"
        steps_en[-1] = "Serve with a fresh salad or bread for a light lunch!"
        steps_es[-1] = "¡Sirve con una ensalada fresca o pan para un almuerzo ligero!"

    # Diet adjustments
    if diet == "vegan":
        steps_en[1] = f"Add plant-based {main} and cook until ready, about 5-7 minutes."
        steps_es[1] = f"Añade {main} basado en plantas y cocina hasta que esté listo, unos 5-7 minutos."
    elif diet == "gluten-free":
        steps_en[3] = "Season with gluten-free spices."
        steps_es[3] = "Sazona con especias sin gluten."
    if time == "quick":
        steps_en[2] = f"Stir in {', '.join(used_extras)} and cook for 3 minutes."
        steps_es[2] = f"Incorpora {', '.join(used_extras)} y cocina por 3 minutos."

    nutrition = {
        "calories": len(all_ingredients) * 150 + 100,
        "protein": len(all_ingredients) * 8 + 5,
        "fat": len(all_ingredients) * 5
    }

    title = title_es if language == 'spanish' else title_en
    steps = steps_es if language == 'spanish' else steps_en
    share_text_en = f"Check out my recipe: {title_en}\nIngredients: {', '.join(all_ingredients)}\nSteps:\n" + \
                    "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps_en)]) + \
                    f"\nNutrition: {nutrition['calories']} kcal, {nutrition['protein']}g protein"
    share_text_es = f"Mira mi receta: {title_es}\nIngredientes: {', '.join(all_ingredients)}\nPasos:\n" + \
                    "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps_es)]) + \
                    f"\nNutrición: {nutrition['calories']} kcal, {nutrition['protein']}g proteína"

    recipe = {
        "title": title,
        "ingredients": all_ingredients,
        "steps": steps,
        "nutrition": nutrition,
        "shareText": share_text_es if language == 'spanish' else share_text_en
    }
    return jsonify(recipe)

# Error handling
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(429)
def too_many_requests(e):
    return jsonify({"error": "Rate limit exceeded, please try again later"}), 429

if __name__ == "__main__":
    CORS(app)  # Allow all origins locally for debugging
    app.run(debug=True)
else:
    CORS(app, resources={r"/generate_recipe": {"origins": "https://recipegenerator-ort9.onrender.com"}})  # Restrict on Render