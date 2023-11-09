import datetime as dt
import uuid
from typing import Annotated

import rq
from fastapi import APIRouter, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api.deps import AdminDep, DbDep, MQDefault
from app.core.config import settings
from app.db import repos as repo
from app.schemas import UserInvite
from app.utils.emails import send_registration_email
from app.utils.exceptions import UserAlreadyActiveException
from app.utils.mocks import mock_worker_job

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
)
async def invite_user(
    db: DbDep,
    mq: MQDefault,
    admin: AdminDep,
    new_invitee: Annotated[UserInvite, Body(...)],
    expires_in_hours: Annotated[
        int,
        Query(
            gt=0,
            alias="expires_in",
            description="hours",
        ),
    ] = 7 * 24,
) -> schemas.WorkerJob:
    """
    ## Invite a user to join Vaultexe server

    ## Permissions
    * Inviter is an admin

    ## Prerequisites
    * The invitee must not be active yet (i.e. never registered before)

    ## Notes
    * A new inactive user will be created for the invitee
    * The invitee will receive an email with a link to activate their account
    * The invitation will expire after 7 days (default)
    * All previous invitations to the invitee will be invalidated
    """
    invitee = await repo.user.get_by_email(db, new_invitee.email)

    if not invitee:
        invitee = await repo.user.create(db, obj_in=new_invitee)
        await db.commit()
        await db.refresh(invitee)
    elif invitee.is_active:
        raise UserAlreadyActiveException
    else:
        await repo.invitation.invalidate_tokens(db, user_id=invitee.id)

    return await setup_inviation(
        mq=mq,
        db=db,
        admin=admin,
        invitee=invitee,
        expires_in_hours=expires_in_hours,
    )


async def setup_inviation(
    *,
    db: AsyncSession,
    mq: rq.Queue,
    admin: models.User,
    invitee: models.User,
    expires_in_hours: int,
) -> schemas.WorkerJob:
    """Handle invitation tokens & invitation email"""
    invitation_token = uuid.uuid4()

    expires_at = dt.datetime.utcnow() + dt.timedelta(hours=expires_in_hours)

    new_invitation = schemas.InvitationCreate(
        token=invitation_token,
        invitee_id=invitee.id,
        created_by=admin.id,
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

    job = mq.enqueue_call(
        func=send_registration_email,
        args=(email_payload,),
        retry=rq.Retry(max=2),
        result_ttl=settings.EMAILS_STATUS_TTL,
    )

    return schemas.WorkerJob.from_rq_job(job)
