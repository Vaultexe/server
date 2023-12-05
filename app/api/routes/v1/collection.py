import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Path, status
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
    rc: AsyncRedisClientDep,
    new_collection: Annotated[schemas.CollectionCreate, Body(...)],
) -> schemas.Collection:
    """
    ## Add new collection

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a create event
    """
    try:
        collection = await repo.collection.create(
            db,
            user_id=user.id,
            obj_in=new_collection,
        )
        await db.commit()
        await db.refresh(collection)
    except IntegrityError:
        await db.rollback()
        raise DuplicateEntityException(models.Collection)

    collection = schemas.Collection.model_validate(collection)
    await notify(rc, user_id=user.id, data=collection, action=Op.CREATE)
    return collection


@router.put("/{collection_id}")
async def update_collection(
    db: DbDep,
    user: UserDep,
    rc: AsyncRedisClientDep,
    collection_id: Annotated[uuid.UUID, Path(...)],
    collection_update: Annotated[schemas.CollectionUpdate, Body(...)],
) -> schemas.Collection:
    """
    ## Update collection

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a update event
    """
    collection = await repo.collection.get(db, id=collection_id)
    if not collection:
        raise EntityNotFoundException("Collection")

    collection.import_from(collection_update)
    await db.commit()
    await db.refresh(collection)

    collection = schemas.Collection.model_validate(collection)
    await notify(rc, user_id=user.id, data=collection, action=Op.UPDATE)
    return collection


@router.delete("/{collection_id}")
async def delete_collection(
    db: DbDep,
    user: UserDep,
    rc: AsyncRedisClientDep,
    collection_id: Annotated[uuid.UUID, Path(...)],
) -> list[uuid.UUID]:
    """
    ## Delete collection & Soft delete all ciphers in it

    ## Overview
    - Delete collection
    - Detach all ciphers from collection and soft delete them
    - Return deleted cipher ids

    ## Sync event
    Syncs user vault by notifying all
    connected devices via redis pubsub
    with a delete event

    ## Client Expectation
    - Client should soft delete all ciphers in collection
    """
    collection = await repo.collection.get(db, id=collection_id)
    if not collection:
        raise EntityNotFoundException("Collection")

    deleted_cipher_ids = await repo.cipher.soft_delete_collection(db, id=collection.id)
    await repo.collection.delete(db, id=collection.id)
    await db.commit()

    collection = schemas.Collection.model_validate(collection)
    await notify(rc, user_id=user.id, data=collection, action=Op.DELETE)
    return deleted_cipher_ids
