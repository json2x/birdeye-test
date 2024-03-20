from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BIRD_EYE_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")