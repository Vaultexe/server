from typing import Literal

from app.schemas import BaseSchema, Cipher, Collection
from app.schemas.enums import Op


class SyncData(BaseSchema):
    """
    Sync data schema
    """

    data: Collection | Cipher
    type: Literal["collection", "cipher"]
    action: Op
