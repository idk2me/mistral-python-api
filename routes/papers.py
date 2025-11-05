from fastapi import APIRouter, status
from utils.db import get_latest_papers, get_paper_by_id, get_all_papers
from utils.mistral_client import summarize_paper
from utils.rss import update_papers
from utils.logging_config import get_logger
from schemas.paper import Paper, UpdatePaper

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def get_papers():
    papers = await get_latest_papers()

    if not papers:
        return status.HTTP_404_NOT_FOUND

    return papers


@router.get("/paper/{id}")
async def get_paper(id: int):
    paper = await get_paper_by_id(id)
    if not paper:
        return {"status": 404, "message": "Paper not found"}
    return paper


@router.get("/allPapers")
async def get_all_papers_route() -> list[Paper]:
    papers = await get_all_papers()
    if not papers:
        return []
    return [Paper(**i) for i in papers]


@router.post("/summarize")
async def summarize_papers(paper: UpdatePaper):
    if not paper.id:
        return {
            "status": 400,
            "message": "No paper in request body",
        }

    summary_data = await summarize_paper(paper.id)

    return summary_data


@router.get("/update")
async def update_papers_endpoint():
    try:
        papers = await update_papers()
        return papers
    except Exception as e:
        logger.error(f"Something went wrong with updating papers: {e}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR
