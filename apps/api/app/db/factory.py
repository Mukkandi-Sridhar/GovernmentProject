from functools import lru_cache

from app.config import get_settings
from app.db.firestore import FirestoreRepository
from app.db.inmemory import InMemoryRepository
from app.db.repository import Repository


@lru_cache
def get_repository() -> Repository:
    settings = get_settings()
    if settings.use_inmemory_db:
        return InMemoryRepository()
    return FirestoreRepository(
        project_id=settings.firebase_project_id,
        credentials_path=settings.google_application_credentials,
    )

