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
    thrad_api_url: str = ""
    overmind_api_key: str = ""
    overmind_project_id: str = ""  # console-only; the Python SDK does NOT read this
    overmind_service_name: str = "sentinel-gate"  # SDK groups traces by this name
    overmind_environment: str = "development"  # SDK env tag (OVERMIND_ENVIRONMENT)
    alpic_token: str = ""
    attestation_private_key_path: str = "./keys/attest_ed25519"
    # PEM contents for hosted deploys where keys/ is never committed.
    attestation_private_key_pem: str = ""
    context_classifier_backend: str = "heuristic"  # heuristic | auto
    context_classifier_block_confidence: float = 0.60
    context_classifier_review_confidence: float = 0.45
    context_classifier_local_files_only: bool = False
    thrad_context_model_id: str = "Thrad/thrad-distilbert-conversation-classifier"
    thrad_context_model_revision: str = "9e7eeadcf69c3f9d286729bb8b6a4f88f7e4faa2"
    # Thrad's model card does not publish tokenizer files; DistilBERT base is the
    # matching tokenizer used for the ONNX inference wrapper.
    thrad_context_tokenizer_id: str = "distilbert-base-uncased"
    port: int = 8000
    env: str = "development"


settings = Settings()
