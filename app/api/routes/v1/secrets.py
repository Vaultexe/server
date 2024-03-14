import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Path
from sqlalchemy.exc import IntegrityError

from app import models, schemas
from app.api.deps import DbDep, UserDep
from app.api.deps.cache import AsyncRedisClientDep
from app.db import repos as repo
from app.events import notify
from app.schemas.enums import Op
from app.utils.exceptions import DuplicateEntityException, EntityNotFoundException

router = APIRouter()


@router.get("/")
async def get_secrets(
    db: DbDep,
    user: UserDep,
) -> list[schemas.Cipher]:
    # TODO: Use pagination
    ciphers = await repo.cipher._get_all(db, user_id=user.id)
    return [schemas.Cipher.model_validate(cipher) for cipher in ciphers]


@router.get("/deleted")
async def get_deleted_secrets(
    db: DbDep,
    user: UserDep,
) -> list[schemas.Cipher]:
    ciphers = await repo.cipher._get_all_deleted(db, user_id=user.id)
    return [schemas.Cipher.model_validate(cipher) for cipher in ciphers]


@router.post("/")
async def create_secret(
    db: DbDep,
    user: UserDep,
    new_cipher: Annotated[schemas.CipherCreate, Body(...)],
    rc: AsyncRedisClientDep,
) -> schemas.Cipher:
    """
    ## Add new secret

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a create event
    """
    try:
        cipher = await repo.cipher.create(
            db,
            user_id=user.id,
            obj_in=new_cipher,
        )
        await db.commit()
        await db.refresh(cipher)
    except IntegrityError:
        await db.rollback()
        raise DuplicateEntityException(models.Cipher)

    cipher = schemas.Cipher.model_validate(cipher)
    await notify(rc, user_id=user.id, data=cipher, action=Op.CREATE)
    return cipher


@router.put("/{cipher_id}")
async def update_secret(
    db: DbDep,
    user: UserDep,
    rc: AsyncRedisClientDep,
    cipher_id: Annotated[uuid.UUID, Path(...)],
    cipher_update: Annotated[schemas.CipherUpdate, Body(...)],
) -> schemas.Cipher:
    """
    ## Update existing secret

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with an update event
    """
    cipher = await repo.cipher.get(db, id=cipher_id)
    if not cipher:
        raise EntityNotFoundException("Secret")

    cipher.import_from(cipher_update)
    await db.commit()
    await db.refresh(cipher)

    secret = schemas.Cipher.model_validate(cipher)
    await notify(rc, user_id=user.id, data=secret, action=Op.UPDATE)
    return secret


@router.put("/restore/{cipher_id}")
async def restore_secret(
    db: DbDep,
    user: UserDep,
    rc: AsyncRedisClientDep,
    cipher_id: Annotated[uuid.UUID, Path(...)],
) -> schemas.Cipher:
    """
    ## Restore soft deleted secret

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a restore event
    """
    cipher = await repo.cipher.restore(db, id=cipher_id)
    if not cipher:
        raise EntityNotFoundException("Secret")
    await db.commit()
    await db.refresh(cipher)

    secret = schemas.Cipher.model_validate(cipher)
    await notify(rc, user_id=user.id, data=secret, action=Op.RESTORE)
    return secret


@router.delete("/{cipher_id}")
async def soft_delete_secret(
    db: DbDep,
    user: UserDep,
    rc: AsyncRedisClientDep,
    cipher_id: Annotated[uuid.UUID, Path(...)],
) -> schemas.Cipher:
    """
    ## Delete existing secret

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a soft delete event
    """
    cipher = await repo.cipher.soft_delete(db, id=cipher_id)
    if not cipher:
        raise EntityNotFoundException("Secret")
    await db.commit()
    await db.refresh(cipher)

    secret = schemas.Cipher.model_validate(cipher)
    await notify(rc, user_id=user.id, data=secret, action=Op.SOFT_DELETE)
    return secret

@router.delete("/{cipher_id}/permanent")
async def permanently_delete_secret(
    db: DbDep,
    user: UserDep,
    rc: AsyncRedisClientDep,
    cipher_id: Annotated[uuid.UUID, Path(...)],
) -> None:
    """
    ## Permanently delete secret

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a delete event
    """
    has_deleted = await repo.cipher.permanent_delete(db, id=cipher_id)
    if not has_deleted:
        raise EntityNotFoundException("Secret")
    await db.commit()
    await notify(rc, user_id=user.id, data=cipher_id, action=Op.DELETE)
