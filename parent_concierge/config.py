from dataclasses import dataclass
from google.genai import types


@dataclass
class ConciergeConfiguration:
    """Configuration for ai models.

    Attributes:
        worker_model (str): Model for working/generation tasks.
    """

    worker_model: str = "gemini-2.5-flash"


retry_config = types.HttpRetryOptions(
    # Backoff tuned for transient Google LLM rate-limit/server responses so
    # retries smooth over occasional 429/5xx errors without long waits.
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

config = ConciergeConfiguration()
