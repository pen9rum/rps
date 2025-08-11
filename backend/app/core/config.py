import os
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

class Settings:
    API_PREFIX: str = "/api/v1"
    CORS_ALLOW_ORIGINS: List[str] = ["*"]  # change to whitelist in prod
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "mock")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

settings = Settings()
