import logging

from langchain_core.prompts import ChatPromptTemplate

from src.deps import get_llm, get_supabase, get_target_chapter_count
from src.state import BookState

logger = logging.getLogger(__name__)


outline_prompt = ChatPromptTemplate.from_template(
    """
You are an expert book planner.

Title: "{title}"

Editor notes before outline:
{notes_on_outline_before}

If there were any notes on a previous outline, follow them carefully:
{notes_on_outline_after}

Requirements:
- Produce a clear numbered outline of chapters (1..{chapter_count}).
- Produce EXACTLY {chapter_count} chapters.
- Each chapter should have a short title and 1-3 bullet points.

Return ONLY the outline text.
"""
)


def generate_outline(state: BookState) -> BookState:
    """
    Generate and store an outline if allowed by gating rules.
    """
    supabase = get_supabase()

    if not state.notes_on_outline_before:
        logger.warning("Missing notes_on_outline_before - cannot generate outline")
        state.control["event"] = "missing_notes_on_outline_before"
        return state

    logger.info("Generating outline...")
    chapter_count = get_target_chapter_count()
    llm = get_llm()
    chain = outline_prompt | llm

    result = chain.invoke(
        {
            "title": state.title,
            "notes_on_outline_before": state.notes_on_outline_before,
            "notes_on_outline_after": state.notes_on_outline_after or "",
            "chapter_count": chapter_count,
        }
    )

    outline_text = result.content.strip()
    state.outline = outline_text

    # Persist in Supabase
    supabase.table("books").update(
        {
            "outline": outline_text,
            "outline_status": "generated",
            "total_chapters": chapter_count,
        }
    ).eq("id", state.book_id).execute()

    # For demo/testing, we force the target chapter count
    state.total_chapters = chapter_count
    logger.info(f"Outline generated. Using chapter_count={chapter_count}")

    state.control["event"] = "outline_generated"
    return state

