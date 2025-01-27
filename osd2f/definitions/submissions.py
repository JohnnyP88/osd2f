from typing import Any, Dict, List

from pydantic import BaseModel


class Submission(BaseModel):
    submission_id: str
    filename: str
    n_deleted: int
    entries: List[Dict[str, Any]]


class SubmissionList(BaseModel):
    """Basically, a list of file submissions as one List."""

    __root__: List[Submission]
