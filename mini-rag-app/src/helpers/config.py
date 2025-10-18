from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_EXTENSIONS: list
    MAX_FILE_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    MONGODB_URI: str
    MONGODB_DATABASE: str
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND:str

    OPENAI_API_KEY:str
    OPENAI_API_URL:str
    COHERE_API_KEY:str

    GENERATION_MODEL_ID:str
    EMBEDDING_MODEL_ID :str
    EMBEDDING_MODEL_SIZE:int

    INPUT_DEFAULT_MAX_CHARACTERS:int
    GENERATION_DEFAULT_MAX_TOKENS:int
    GENERATION_DEFAULT_TEMPERATURE:float

    VECTOR_DB_BACKEND:str
    VECTOR_DB_PATH:str
    VECTOR_DB_DISTANCE_METHOD:str
    class config:
        env_file = load_dotenv(find_dotenv())



def get_settings() -> Settings:
    return Settings()