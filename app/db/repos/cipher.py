from app import models, schemas
from app.db.repos.base import BaseRepo


class CipherRepo(BaseRepo[models.Cipher, schemas.CipherCreate]):
    """Cipher repo"""


cipher = CipherRepo(models.Cipher)
