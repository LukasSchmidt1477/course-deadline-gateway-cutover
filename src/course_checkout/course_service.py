"""Application-shaped entry point for course delivery reporting."""

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from .deadline_register import (
    CourseDeliveryRequest,
    DeliverySnapshot,
    build_delivery_snapshot,
)
from .educator_report import InfraiEducatorReporter

service = FastAPI(title="Course delivery register")


class EducatorReportResponse(BaseModel):
    delivery: DeliverySnapshot
    educator_report: str


def get_reporter() -> InfraiEducatorReporter:
    return InfraiEducatorReporter()


@service.post("/educator-reports", response_model=EducatorReportResponse)
def create_educator_report(
    request: CourseDeliveryRequest,
    reporter: InfraiEducatorReporter = Depends(get_reporter),
) -> EducatorReportResponse:
    snapshot = build_delivery_snapshot(request)
    return EducatorReportResponse(
        delivery=snapshot,
        educator_report=reporter.write(snapshot),
    )
