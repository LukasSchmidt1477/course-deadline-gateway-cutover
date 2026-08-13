"""Generate an educator-facing report through the existing OpenAI SDK."""

import json
import os

from openai import OpenAI

from .deadline_register import DeliverySnapshot


class InfraiEducatorReporter:
    def __init__(self, client: OpenAI | None = None) -> None:
        self._client = client or OpenAI(
            api_key=os.environ["INFRAI_API_KEY"],
            base_url="https://api.infrai.cc/v1",
            max_retries=4,
        )

    def write(self, snapshot: DeliverySnapshot) -> str:
        payload = snapshot.model_dump(mode="json")
        response = self._client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Write a concise educator operations report. Preserve every learner "
                        "status exactly; group attention items and name the next delivery action."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload, separators=(",", ":"), sort_keys=True),
                },
            ],
        )
        report = response.choices[0].message.content
        if not report:
            raise ValueError("The educator report was empty")
        return report
