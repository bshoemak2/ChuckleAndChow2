from config import cache
import logging

def get_cached_recipe(key):
    """Retrieve a cached recipe if available."""
    cached_data = cache.get(key)
    if cached_data:
        logging.debug(f"Cache hit for key: {key}")
    else:
        logging.debug(f"Cache miss for key: {key}")
    return cached_data

def cache_recipe(key, data, timeout=3600):
    """Store recipe data in cache with a timeout."""
    cache.set(key, data, timeout=timeout)
    logging.debug(f"Cached recipe with key: {key}")

def clear_cache():
    """Clear all cached recipes."""
    cache.clear()
    logging.info("Cache cleared successfully")