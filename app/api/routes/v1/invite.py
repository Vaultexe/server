import datetime as dt
import uuid
from typing import Annotated

import rq
from fastapi import APIRouter, Body, Query, status

from app import schemas
from app.api.deps import AsyncRedisClientDep, SyncRedisClientDep, dbDep
from app.core.config import settings
from app.db import repos as repo
from app.schemas import UserInvite
from app.schemas.enums import WorkerQueue
from app.utils.emails import send_registration_email
from app.utils.exceptions import UserAlreadyActiveException
from app.utils.mocks import mock_worker_job

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    # TODO: add admin dep permission
)
async def invite_user(
    db: dbDep,
    rc: AsyncRedisClientDep,
    rc_sync: SyncRedisClientDep,
    new_invitee: Annotated[UserInvite, Body(...)],
    expires_in_hours: Annotated[
        int,
        Query(
            gt=0,
            alias="expires_in",
            description="hours",
        ),
    ] = 7
    * 24,
) -> schemas.WorkerJob:
    """
    ### Invite a user to join Vaultexe server

    ### Permissions
    * Inviter is an admin

    ### Prerequisites
    * The invitee must not be active yet (i.e. never registered before)

    ### Notes
    * A new inactive user will be created for the invitee
    * The invitee will receive an email with a link to activate their account
    * The invitation will expire after 7 days (default)
    * All previous invitations to the invitee will be invalidated
    """
    invitee = await repo.user.get_by_email(db, new_invitee.email)

    if not invitee:
        invitee = await repo.user.create(db, obj_in=new_invitee)
    elif invitee.is_active:
        raise UserAlreadyActiveException

    await repo.invitation.invalidate_tokens(db, user_id=invitee.id)

    invitation_token = uuid.uuid4()

    expires_at = dt.datetime.utcnow() + dt.timedelta(hours=expires_in_hours)

    new_invitation = schemas.InvitationCreate(
        token=invitation_token,
        invitee_id=invitee.id,
        created_by=invitee.id,  # TODO: get current admin id from request
        expires_at=expires_at,
    )

    await repo.invitation.create(db, obj_in=new_invitation)

    await db.commit()

    if not settings.email_enabled:
        return mock_worker_job(invitation_token=invitation_token)

    email_payload = schemas.RegistrationEmailPayload(
        to=invitee.email,
        token=invitation_token.hex,
        expires_in_hours=expires_in_hours,
    )

    q = rq.Queue(WorkerQueue.LOW.value, connection=rc_sync)

    job = q.enqueue_call(
        func=send_registration_email,
        args=(email_payload,),
        retry=rq.Retry(max=2),
        result_ttl=settings.EMAILS_STATUS_TTL,
    )

    return schemas.WorkerJob.from_rq_job(job)
