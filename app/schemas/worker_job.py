import datetime as dt
from typing import Any, Self

import rq
from pydantic import ConfigDict

from app.schemas import BaseSchema
from app.schemas.enums import WorkerQueue


class WorkerJob(BaseSchema):
    id: str
    created_at: dt.datetime
    started_at: dt.datetime | None
    ended_at: dt.datetime | None
    enqueued_at: dt.datetime | None
    worker_queue_level: WorkerQueue
    status: rq.job.JobStatus
    result_ttl: int | None
    result: Any | None

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_rq_job(cls, job: rq.job.Job) -> Self:
        return cls(
            id=job.get_id(),
            created_at=job.created_at,
            started_at=job.started_at,
            ended_at=job.ended_at,
            enqueued_at=job.enqueued_at,
            worker_queue_level=WorkerQueue(job.origin),
            status=job.get_status(),
            result_ttl=job.result_ttl,
            result=job.result,
        )
