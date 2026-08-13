from datetime import datetime

from course_checkout.deadline_register import (
    CourseDeliveryRequest,
    SubmissionStatus,
    build_delivery_snapshot,
)


def test_snapshot_separates_completed_and_attention_orders() -> None:
    request = CourseDeliveryRequest(
        course_id="checkout-ops-101",
        course_title="Storefront checkout operations",
        deadline=datetime.fromisoformat("2026-09-15T17:00:00+08:00"),
        observed_at=datetime.fromisoformat("2026-09-16T09:00:00+08:00"),
        learners=[
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
            {
                "learner_id": "learner-31",
                "learner_name": "Noor",
                "submitted_at": "2026-09-15T18:05:00+08:00",
            },
        ],
    )

    snapshot = build_delivery_snapshot(request)

    assert [learner.status for learner in snapshot.learners] == [
        SubmissionStatus.ON_TIME,
        SubmissionStatus.OVERDUE,
        SubmissionStatus.LATE,
    ]

