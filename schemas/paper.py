from pydantic import BaseModel
from datetime import datetime


class Paper(BaseModel):
    id: int | None = None
    arxiv_id: str
    title: str
    summary: str
    authors: str
    published: str
    category: str
    link: str
    processed: bool = False
    ai_summary: str | None = None
    novelty_score: int | None = None
    relevance_score: int | None = None
    read_recommendation: str | None = None
    viewed: bool = False
    created_at: datetime | None = None


class UpdatePaper(BaseModel):
    id: int | None = None


class GetPaper(BaseModel):
    id: int | None = None


class UserSettings(BaseModel):
    niche_interests: str
    additional_params: str
