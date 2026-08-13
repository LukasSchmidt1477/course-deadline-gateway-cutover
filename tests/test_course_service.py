from fastapi.testclient import TestClient

from course_checkout.course_service import get_reporter, service
from course_checkout.deadline_register import DeliverySnapshot


class RecordingReporter:
    def __init__(self) -> None:
        self.snapshot: DeliverySnapshot | None = None

    def write(self, snapshot: DeliverySnapshot) -> str:
        self.snapshot = snapshot
        return "Mina submitted on time. Ravi needs an educator follow-up."


def test_route_passes_deadline_decisions_to_reporter() -> None:
    reporter = RecordingReporter()
    service.dependency_overrides[get_reporter] = lambda: reporter
    try:
        response = TestClient(service).post(
            "/educator-reports",
            json={
                "course_id": "checkout-ops-101",
                "course_title": "Storefront checkout operations",
                "deadline": "2026-09-15T17:00:00+08:00",
                "observed_at": "2026-09-16T09:00:00+08:00",
                "learners": [
                    {
                        "learner_id": "learner-17",
                        "learner_name": "Mina",
                        "submitted_at": "2026-09-15T16:42:00+08:00",
                    },
                    {
                        "learner_id": "learner-23",
                        "learner_name": "Ravi",
                        "submitted_at": None,
                    },
                ],
            },
        )
    finally:
        service.dependency_overrides.clear()

    assert response.status_code == 200
    assert reporter.snapshot is not None
    assert [item.status.value for item in reporter.snapshot.learners] == [
        "on_time",
        "overdue",
    ]
    assert response.json()["educator_report"].startswith("Mina submitted")

