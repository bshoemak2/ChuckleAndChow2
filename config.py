import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="recipe_generator.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
CORS(app, supports_credentials=True)

# Initialize services
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day", "10 per minute"], storage_uri="memory://")
cache = Cache(app, config={"CACHE_TYPE": "simple"})