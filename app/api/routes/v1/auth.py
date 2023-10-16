from typing import Annotated

from fastapi import APIRouter, Body, Path, Response, status

from app.api.deps import (
    dbDep,
)
from app.db import repos as repo
from app.utils.exceptions import (
    AuthorizationException,
    UserAlreadyActiveException,
    UserNotFoundException,
)

router = APIRouter()


@router.post(
    "/register/{registration_token}",
    response_class=Response,
    status_code=status.HTTP_200_OK,
)
async def register(
    db: dbDep,
    registration_token: Annotated[str, Path(...)],
    password: Annotated[
        str,
        Body(
            ...,
            description="Double KDF hash of master password",
        ),
    ],
) -> None:
    """
    ### Register by setting a new password

    ### Prerequisites
    * User account invited by admin
    * User has not been activated account yet

    ### Overview
    * Validates registration token
    * Validates user account
    * Hashes & sets the new user password (already double KDF hashed by client)
    * Activates user account
    * Invalidates token
    """
    invitation = await repo.invitation.get_by_token(db, token=registration_token)

    if not invitation or not invitation.is_valid:
        raise AuthorizationException

    invitee = await repo.user.get(db, id=invitation.invitee_id)

    if not invitee:
        raise UserNotFoundException

    if invitee.is_active:
        raise UserAlreadyActiveException

    invitee.update_password(password).activate()

    await repo.invitation.invalidate_tokens(db, user_id=invitee.id)

    await db.commit()
