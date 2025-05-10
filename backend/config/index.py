import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    REDDIT_CLIENT_ID = os.getenv("reddit_client_id")
    REDDIT_CLIENT_SECRET = os.getenv("reddit_client_secret")
    REDDIT_USER_AGENT = os.getenv("reddit_user_agent")
    FRONTEND_URL = os.getenv("frontend_url")
