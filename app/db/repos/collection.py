from app import models, schemas
from app.db.repos.base import BaseRepo


class CollectionRepo(BaseRepo[models.Collection, schemas.CollectionCreate]):
    """Cipher repo"""


cipher = CollectionRepo(models.Collection)
