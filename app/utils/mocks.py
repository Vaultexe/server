import rq

from app import schemas
from app.schemas import enums


def mock_worker_job(**kwargs) -> schemas.WorkerJob:
    return schemas.WorkerJob(
        id="1",
        created_at="2021-01-01 00:00:00",
        started_at="2021-01-01 00:00:00",
        ended_at="2021-01-01 00:00:00",
        enqueued_at="2021-01-01 00:00:00",
        result="result",
        result_ttl=1,
        status=rq.job.JobStatus.QUEUED,
        worker_queue_level=enums.WorkerQueue.DEFAULT,
        **kwargs,
    )
