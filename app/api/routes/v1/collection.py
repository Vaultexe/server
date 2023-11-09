import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Path, status

from app import models, schemas
from app.api.deps import DbDep, UserDep
from app.db import repos as repo
from app.utils.exceptions import DuplicateEntityException, EntityNotFoundException

router = APIRouter()


@router.get("/")
async def get_collections(
    db: DbDep,
    user: UserDep,
) -> list[schemas.Collection]:
    # TODO: Use pagination
    collections = await repo.collection._get_all(db, user_id=user.id)
    return [schemas.Collection.model_validate(collection) for collection in collections]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "Collection already exists"},
        status.HTTP_201_CREATED: {"description": "Collection created"},
    },
)
async def create_collection(
    db: DbDep,
    user: UserDep,
    new_collection: Annotated[schemas.CollectionCreate, Body(...)],
) -> schemas.Collection:
    try:
        collection = await repo.collection.create(
            db,
            user_id=user.id,
            obj_in=new_collection,
        )
        await db.commit()
        await db.refresh(collection)
        return schemas.Collection.model_validate(collection)
    except Exception:
        await db.rollback()
        raise DuplicateEntityException(models.Collection)


@router.put("/{collection_id}")
async def update_collection(
    db: DbDep,
    _: UserDep,
    collection_id: Annotated[uuid.UUID, Path(...)],
    collection_update: Annotated[schemas.CollectionUpdate, Body(...)],
) -> schemas.Collection:
    collection = await repo.collection.get(db, id=collection_id)
    if not collection:
        raise EntityNotFoundException("Collection")
    collection.import_from(collection_update)
    await db.commit()
    await db.refresh(collection)
    return schemas.Collection.model_validate(collection)


@router.delete("/{collection_id}")
async def delete_collection(
    db: DbDep,
    _: UserDep,
    collection_id: Annotated[uuid.UUID, Path(...)],
) -> list[uuid.UUID]:
    """
    ## Delete collection & Soft delete all ciphers in it

    ## Overview
    - Delete collection
    - Detach all ciphers from collection and soft delete them
    - Return deleted cipher ids
    """
    collection = await repo.collection.get(db, id=collection_id)
    if not collection:
        raise EntityNotFoundException("Collection")
    deleted_cipher_ids = await repo.cipher.soft_delete_collection(
        db,
        collection_id=collection.id,
    )
    await repo.collection.delete(db, id=collection.id)
    await db.commit()
    return deleted_cipher_ids
