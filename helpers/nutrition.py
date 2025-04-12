import random

def calculate_nutrition(ingredients):
    try:
        return {"calories": random.randint(100, 1000), "protein": random.randint(10, 50)}
    except Exception as e:
        return {"error": str(e)}