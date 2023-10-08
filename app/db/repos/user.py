from app import models, schemas
from app.db.repos.base import BaseRepo


class UserRepo(BaseRepo[models.User, schemas.UserInvite]):
    """User repo"""


cipher = UserRepo(models.User)
