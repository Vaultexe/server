import datetime as dt

import rq

from app import schemas
from app.schemas import enums


def mock_worker_job(**kwargs) -> schemas.WorkerJob:
    return schemas.WorkerJob(
        id="1",
        created_at=dt.datetime.now(dt.UTC),
        started_at=dt.datetime.now(dt.UTC),
        enqueued_at=dt.datetime.now(dt.UTC),
        ended_at=dt.datetime.now(dt.UTC) + dt.timedelta(seconds=1),
        result="result",
        result_ttl=1,
        status=rq.job.JobStatus.QUEUED,
        worker_queue_level=enums.WorkerQueue.DEFAULT,
        **kwargs,
    )
