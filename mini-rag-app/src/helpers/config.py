from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_EXTENSIONS: list
    MAX_FILE_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    class config:
        env_file = load_dotenv(find_dotenv())



def get_settings() -> Settings:
    return Settings()