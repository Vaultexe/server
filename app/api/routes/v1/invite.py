import datetime as dt
import uuid
from typing import Annotated

import pandas as pd
import rq
from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile, status
from pydantic import validate_email
from pydantic_core import PydanticCustomError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api.deps import AdminDep, DbDep, MQDefault
from app.core.config import settings
from app.db import repos as repo
from app.schemas import UserInvite
from app.utils.emails import send_registration_email
from app.utils.exceptions import InvalidFileTypeException, UserAlreadyActiveException
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


@router.post(
    "/bulk",
    status_code=status.HTTP_202_ACCEPTED,
)
async def bulk_invite_users(
    db: DbDep,
    mq: MQDefault,
    admin: AdminDep,
    are_admin: Annotated[bool, Query(description="Are the invitees admins?")],
    sheet: Annotated[
        UploadFile,
        File(
            ...,
            description="""
            CSV file of invitees emails
            emails need to be in the first column of the first sheet
            """,
        ),
    ],
    expires_in_hours: Annotated[
        int,
        Query(
            gt=0,
            alias="expires_in",
            description="hours",
        ),
    ] = 7 * 24,
):
    """
    ## Invite multiple users to join Vaultexe server

    ## Permissions
    * Inviter is an admin

    ## Prerequisites
    * The invitees must not be active yet (i.e. never registered before)

    ## Notes
    * File must be an excel file
    * A new inactive user will be created for each invitee
    * Each invitee will receive an email with a link to activate their account
    * The invitation will expire after 7 days (default)
    * All previous invitations to the invitees will be invalidated
    """
    emails = read_validated_emails(sheet)

    user_invites = [UserInvite(email=email, is_admin=are_admin) for email in emails]

    invitees = await repo.user.bulk_create(db, objs_in=user_invites)
    await db.commit()
    for invitee in invitees:
        await db.refresh(invitee)

    invitees = [invitee for invitee in invitees if not invitee.is_active]
    await repo.invitation.invalidate_bulk_tokens(db, user_ids=[inv.id for inv in invitees])

    await setup_bulk_inviations(
        mq=mq,
        db=db,
        admin=admin,
        invitees=invitees,
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
    expires_at = dt.datetime.now(dt.UTC) + dt.timedelta(hours=expires_in_hours)

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


async def setup_bulk_inviations(
    *,
    db: AsyncSession,
    mq: rq.Queue,
    admin: models.User,
    invitees: list[models.User],
    expires_in_hours: int,
) -> None:
    """Handle invitation tokens & invitation emails"""
    invitation_tokens = [uuid.uuid4() for _ in range(len(invitees))]
    expires_at = dt.datetime.now(dt.UTC) + dt.timedelta(hours=expires_in_hours)

    new_invitations = [
        schemas.InvitationCreate(
            token=token,
            invitee_id=invitee.id,
            created_by=admin.id,
            expires_at=expires_at,
        )
        for token, invitee in zip(invitation_tokens, invitees, strict=True)
    ]

    await repo.invitation.bulk_create(db, objs_in=new_invitations)
    await db.commit()

    if not settings.email_enabled:
        return

    email_payloads = [
        schemas.RegistrationEmailPayload(
            to=invitee.email,
            token=token.hex,
            expires_in_hours=expires_in_hours,
        )
        for token, invitee in zip(invitation_tokens, invitees, strict=True)
    ]

    mq.enqueue_many(
        [
            rq.Queue.prepare_data(
                func=send_registration_email,
                args=(payload,),
                retry=rq.Retry(max=2),
                result_ttl=settings.EMAILS_STATUS_TTL,
            )
            for payload in email_payloads
        ]
    )



def read_validated_emails(sheet: UploadFile) -> list[str]:
    try:
        content = pd.read_excel(sheet.file, header=None).values.flatten().tolist()
    except Exception:
        raise InvalidFileTypeException("excel")
    return get_validate_emails(content)


def get_validate_emails(emails: list[str]) -> list[str]:
    for i in range(len(emails)):
        try:
            _, emails[i] = validate_email(emails[i])
        except PydanticCustomError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email at line {i}: {emails[i]}",
            )
    return emails
