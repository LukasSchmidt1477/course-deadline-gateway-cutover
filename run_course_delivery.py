"""Run one course delivery through the service boundary."""

from fastapi.testclient import TestClient

from course_checkout.course_service import service


def main() -> None:
    request = {
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
    }
    response = TestClient(service).post("/educator-reports", json=request)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()

