import os

from dotenv import load_dotenv

load_dotenv()

LINKEDIN_CSRF_TOKEN = os.environ["LINKEDIN_CSRF_TOKEN"]
LINKEDIN_COOKIE = os.environ["LINKEDIN_COOKIE"]

BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")

ENV = os.environ["ENV"]
