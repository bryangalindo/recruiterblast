import os

from dotenv import load_dotenv

load_dotenv()

LINKEDIN_CSRF_TOKEN = os.environ["LINKEDIN_CSRF_TOKEN"]
LINKEDIN_COOKIE = os.environ["LINKEDIN_COOKIE"]
