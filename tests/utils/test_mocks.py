from app import schemas
from app.utils.mocks import mock_worker_job


def test_mock_worker_job():
    # Arrange
    kwargs = {"extra_attr": "extra_attr"}

    # Act
    worker_job = mock_worker_job(**kwargs)

    # Assert
    assert isinstance(worker_job, schemas.WorkerJob)
    for key, value in kwargs.items():
        assert getattr(worker_job, key) == value

