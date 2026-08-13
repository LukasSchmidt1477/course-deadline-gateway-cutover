"""Deterministic course delivery and learner deadline decisions."""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class SubmissionStatus(str, Enum):
    ON_TIME = "on_time"
    LATE = "late"
    DUE = "due"
    OVERDUE = "overdue"


class LearnerDelivery(BaseModel):
    learner_id: str = Field(min_length=1)
    learner_name: str = Field(min_length=1)
    submitted_at: datetime | None = None


class CourseDeliveryRequest(BaseModel):
    course_id: str = Field(min_length=1)
    course_title: str = Field(min_length=1)
    deadline: datetime
    observed_at: datetime
    learners: list[LearnerDelivery] = Field(min_length=1)

    @model_validator(mode="after")
    def require_aware_timestamps(self) -> "CourseDeliveryRequest":
        timestamps = [self.deadline, self.observed_at]
        timestamps.extend(
            learner.submitted_at
            for learner in self.learners
            if learner.submitted_at is not None
        )
        if any(value.tzinfo is None or value.utcoffset() is None for value in timestamps):
            raise ValueError("deadline, observed_at, and submitted_at must include a timezone")
        return self


class LearnerDeadline(BaseModel):
    learner_id: str
    learner_name: str
    status: SubmissionStatus


class DeliverySnapshot(BaseModel):
    course_id: str
    course_title: str
    deadline: datetime
    observed_at: datetime
    learners: list[LearnerDeadline]


def classify_submission(
    *, deadline: datetime, observed_at: datetime, submitted_at: datetime | None
) -> SubmissionStatus:
    deadline_utc = deadline.astimezone(timezone.utc)
    if submitted_at is not None:
        return (
            SubmissionStatus.ON_TIME
            if submitted_at.astimezone(timezone.utc) <= deadline_utc
            else SubmissionStatus.LATE
        )
    return (
        SubmissionStatus.DUE
        if observed_at.astimezone(timezone.utc) <= deadline_utc
        else SubmissionStatus.OVERDUE
    )


def build_delivery_snapshot(request: CourseDeliveryRequest) -> DeliverySnapshot:
    learners = [
        LearnerDeadline(
            learner_id=learner.learner_id,
            learner_name=learner.learner_name,
            status=classify_submission(
                deadline=request.deadline,
                observed_at=request.observed_at,
                submitted_at=learner.submitted_at,
            ),
        )
        for learner in request.learners
    ]
    return DeliverySnapshot(
        course_id=request.course_id,
        course_title=request.course_title,
        deadline=request.deadline,
        observed_at=request.observed_at,
        learners=learners,
    )

