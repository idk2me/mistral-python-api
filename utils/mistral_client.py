from utils.settings import settings
from utils.logging_config import get_logger
from utils.db import get_paper_by_id, update_paper_summary, get_user_settings
from mistralai import Mistral
import json
import asyncio

logger = get_logger(__name__)

client = Mistral(api_key=settings.mistral_api_key)


async def summarize_paper(id: int) -> dict:
    paper = await get_paper_by_id(id)
    paper = dict(paper)
    title = paper.get("title")
    abstract = paper.get("summary")

    user_settings = await get_user_settings()
    niche_interests = user_settings.get(
        "niche_interests",
        "Just be general",
    )
    additional_params = user_settings.get(
        "additional_params",
        "Highlight research significance to the field as a whole",
    )

    prompt = f"""
    You are a highly critical AI research assistant evaluating papers for an advanced LLM researcher.
    Be selective and skeptical — most papers are incremental and not worth full attention.

    User focus:
    - Research niche: {niche_interests}
    - Summary focus: {additional_params}

    Your task:
    1. Summarize the paper in 4–5 sentences, emphasizing information most relevant to the user's focus.
    2. Evaluate the paper’s novelty and relevance on a scale of 1–10.
        - **Novelty (1–10):** How original or groundbreaking is the work? Penalize rehashed methods or minor extensions.
        - **Relevance (1–10):** How directly important is this to advancing core LLM research or to the user’s interests?
    3. Provide a **recommendation** based on these criteria:
        - "Yes" → Both novelty ≥ 8 and relevance ≥ 8 (breakthrough or highly relevant)
        - "Maybe" → Either novelty or relevance 5–7 (solid but incremental)
        - "No" → Both novelty and relevance < 5 (derivative, niche, or unimpactful)
    4. Explain *briefly* why you gave these scores.

    Return **only strict JSON** in this format (no extra commentary):
    {{
        "summary": "string",
        "novelty": int,
        "relevance": int,
        "recommendation": "Yes | Maybe | No",
        "reasoning": "string (one-sentence justification for your evaluation)"
    }}

    Title: {title}

    Abstract:
    {abstract}
    """
    data = None
    try:
        res = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "content": prompt,
                    "role": "user",
                }
            ],
        )
        content = res.choices[0].message.content
        logger.info(f"Mistral response: {content}")

        if content.strip().startswith("```"):
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            data = {
                "summary": content.strip(),
                "novelty": None,
                "relevance": None,
                "recommendation": None,
            }
        summary_data = {
            "ai_summary": data.get("summary", "").strip(),
            "novelty_score": int(data.get("novelty")) if data.get("novelty") else None,
            "relevance_score": (
                int(data.get("relevance")) if data.get("relevance") else None
            ),
            "read_recommendation": data.get("recommendation"),
        }
        await update_paper_summary(paper["arxiv_id"], summary_data)
        paper.update(summary_data)
        return paper
    except Exception as e:
        logger.error(f"Error summarizing paper {id}: {e}")
        summary_data = {
            "ai_summary": None,
            "novelty_score": None,
            "relevance_score": None,
            "read_recommendation": None,
        }
        await update_paper_summary(paper["arxiv_id"], summary_data)
        paper.update(summary_data)
        return paper
