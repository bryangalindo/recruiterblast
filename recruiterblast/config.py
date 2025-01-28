import os

from dotenv import load_dotenv

load_dotenv()

LINKEDIN_CSRF_TOKEN = os.environ["LINKEDIN_CSRF_TOKEN"]
LINKEDIN_COOKIE = os.environ["LINKEDIN_COOKIE"]

BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")

GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_CUSTOM_SEARCH_ENGINE_ID = os.getenv(
    "GOOGLE_SEARCH_CUSTOM_SEARCH_ENGINE_ID"
)

ENV = os.environ["ENV"]
