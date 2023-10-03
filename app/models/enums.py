from sqlalchemy.dialects import postgresql as pg

from app.schemas.enums import CipherType

PgCipherType = pg.ENUM(CipherType, name="cipher_type")
