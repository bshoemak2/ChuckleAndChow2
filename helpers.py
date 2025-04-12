import logging

def validate_input(data):
    """Validate incoming JSON data for recipe generation."""
    if not isinstance(data, dict):
        raise ValueError("Request data must be a dictionary")
    ingredients = data.get('ingredients', [])
    preferences = data.get('preferences', {})
    if not isinstance(ingredients, list) or not isinstance(preferences, dict):
        raise ValueError("Ingredients must be a list and preferences a dictionary")
    if len(ingredients) > 10:
        raise ValueError("Maximum of 10 ingredients allowed")
    return ingredients, preferences

def calculate_nutrition(ingredients):
    """Simple nutrition calculation based on ingredient count."""
    return {
        "calories": 300 + len(ingredients) * 50,
        "protein": 20 + len(ingredients) * 5,
        "fat": 10 + len(ingredients) * 3
    }

def generate_share_text(recipe, language, is_predefined=False):
    """Generate shareable text for a recipe."""
    title = recipe['title']
    ingredients = ", ".join(recipe['ingredients'])
    steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(recipe['steps'])])
    nutrition = f"Calories: {recipe['nutrition']['calories']} kcal, Protein: {recipe['nutrition']['protein']}g"
    
    if language == 'spanish':
        return f"Mira mi receta: {title}\nIngredientes: {ingredients}\nPasos:\n{steps}\nNutrición: {nutrition}"
    return f"Check out my recipe: {title}\nIngredients: {ingredients}\nSteps:\n{steps}\nNutrition: {nutrition}"