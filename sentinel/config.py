"""Central config. All secrets/settings load from environment (.env).

Never hardcode keys; never log the values here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    tavily_api_key: str = ""
    thrad_api_key: str = ""
    overmind_api_key: str = ""
    overmind_project_id: str = ""
    alpic_token: str = ""
    attestation_private_key_path: str = "./keys/attest_ed25519"
    port: int = 8000
    env: str = "development"


settings = Settings()
