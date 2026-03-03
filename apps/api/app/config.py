from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AP Civic AI API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_base_url: str = "http://localhost:8000"

    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "huggingface"
    huggingface_api_token: str | None = None
    huggingface_embedding_model: str = "BAAI/bge-m3"
    huggingface_inference_url: str = "https://api-inference.huggingface.co/pipeline/feature-extraction"

    firebase_project_id: str | None = None
    google_application_credentials: str | None = None
    gcs_bucket_name: str | None = None

    use_inmemory_db: bool = True
    disable_auth: bool = True

    allowed_schemes: tuple[str, ...] = ("https",)
    crawl_timeout_seconds: int = 25
    crawl_max_pages_per_host: int = 30
    crawl_max_depth: int = 2
    crawl_user_agent: str = "APCivicAI/1.0 (+https://ap-civic.example)"

    scheduler_enabled: bool = True
    scheduler_cron_hour: int = 3
    scheduler_cron_minute: int = 0

    request_timeout_seconds: int = 40
    rate_limit_per_minute: int = 60
    rate_limit_chat_query_per_minute: int = 60
    rate_limit_chat_jobs_per_minute: int = 120
    rate_limit_admin_per_minute: int = 60

    faiss_index_path: str = "./data/faiss.index"
    faiss_meta_path: str = "./data/faiss_meta.json"

    stale_data_hours: int = 48
    enable_agent_orchestration: bool = False
    open_source_seed_hosts: tuple[str, ...] = (
        "ap.gov.in",
        "jnanabhumi.ap.gov.in",
        "socialwelfare.ap.gov.in",
        "scholarships.gov.in",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
