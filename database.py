import sqlite3
import json
import os
import logging

DATABASE_FILE = 'recipes.db'

# Expanded flavor pairing dictionary
FLAVOR_PAIRS = {
    "chicken": ["garlic", "onion", "lime", "cilantro", "curry", "ginger", "soy sauce", "rosemary", "thyme", "paprika"],
    "tofu": ["soy sauce", "ginger", "garlic", "sesame oil", "chili", "peanuts", "scallions"],
    "beef": ["mushrooms", "onion", "garlic", "rosemary", "thyme", "red wine", "black pepper"],
    "shrimp": ["garlic", "lemon", "chili", "cilantro", "lime", "butter", "parsley"],
    "bacon": ["egg", "onion", "garlic", "cheese", "potatoes", "black pepper", "thyme"],
    "egg": ["bacon", "cheese", "onion", "spinach", "tomatoes", "chives", "black pepper"],
    "pork": ["apple", "onion", "garlic", "thyme", "rosemary", "mustard", "sage"],
    "fish": ["lemon", "dill", "garlic", "olive oil", "capers", "parsley", "white wine"],
    "salmon": ["lemon", "dill", "garlic", "honey", "soy sauce", "ginger", "sesame"],
    "lamb": ["rosemary", "garlic", "thyme", "mint", "red wine", "cumin", "yogurt"]
}

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE_FILE):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            if count > 0:
                logging.info(f"Recipes table already has {count} entries")
                return

    logging.info("Recipes table is empty, populating with initial data")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_en TEXT NOT NULL,
                title_es TEXT NOT NULL,
                steps_en TEXT NOT NULL,
                steps_es TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                nutrition TEXT NOT NULL,
                cooking_time INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                rating REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0
            )
        ''')

        initial_recipes = [
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
                "ingredients": ["tofu", "ginger", "soy sauce"],
                "nutrition": {"calories": 320, "protein": 18, "fat": 12},
                "cooking_time": 15,
                "difficulty": "easy"
            },
            # ... (other recipes unchanged for brevity, assume all 15 are here)
        ]

        for recipe in initial_recipes:
            cursor.execute('''
                INSERT INTO recipes (title_en, title_es, steps_en, steps_es, ingredients, nutrition, cooking_time, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe['title_en'],
                recipe['title_es'],
                json.dumps(recipe['steps_en']),
                json.dumps(recipe['steps_es']),
                json.dumps(recipe['ingredients']),
                json.dumps(recipe['nutrition']),
                recipe['cooking_time'],
                recipe['difficulty']
            ))
        conn.commit()
        logging.info(f"Inserted {len(initial_recipes)} recipes into the database")

def get_all_recipes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes")
        rows = cursor.fetchall()
        recipes = []
        for row in rows:
            recipes.append({
                "id": row['id'],
                "title_en": row['title_en'],
                "title_es": row['title_es'],
                "steps_en": json.loads(row['steps_en']),
                "steps_es": json.loads(row['steps_es']),
                "ingredients": json.loads(row['ingredients']),
                "nutrition": json.loads(row['nutrition']),
                "cooking_time": row['cooking_time'],
                "difficulty": row['difficulty'],
                "rating": row['rating'],
                "rating_count": row['rating_count']
            })
        return recipes

def get_flavor_pairs():
    return FLAVOR_PAIRS