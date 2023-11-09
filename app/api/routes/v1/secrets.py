import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Path

from app import models, schemas
from app.api.deps import DbDep, UserDep
from app.db import repos as repo
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


@router.post("/")
async def create_secret(
    db: DbDep,
    user: UserDep,
    new_cipher: Annotated[schemas.CipherCreate, Body(...)],
) -> schemas.Cipher:
    try:
        cipher = await repo.cipher.create(
            db,
            user_id=user.id,
            obj_in=new_cipher,
        )
        await db.commit()
        await db.refresh(cipher)
        return schemas.Cipher.model_validate(cipher)
    except Exception:
        await db.rollback()
        raise DuplicateEntityException(models.Cipher)


@router.put("/{cipher_id}")
async def update_secret(
    db: DbDep,
    _: UserDep,
    cipher_id: Annotated[uuid.UUID, Path(...)],
    cipher_update: Annotated[schemas.CipherUpdate, Body(...)],
) -> schemas.Cipher:
    cipher = await repo.cipher.get(db, id=cipher_id)
    if not cipher:
        raise EntityNotFoundException("Secret")
    cipher.import_from(cipher_update)
    await db.commit()
    await db.refresh(cipher)
    return schemas.Cipher.model_validate(cipher)


@router.delete("/{cipher_id}")
async def delete_secret(
    db: DbDep,
    _: UserDep,
    cipher_id: Annotated[uuid.UUID, Path(...)],
) -> schemas.Cipher:
    cipher = await repo.cipher.soft_delete(db, id=cipher_id)
    if not cipher:
        raise EntityNotFoundException("Secret")
    await db.commit()
    await db.refresh(cipher)
    return schemas.Cipher.model_validate(cipher)
