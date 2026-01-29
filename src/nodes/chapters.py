import logging

from langchain_core.prompts import ChatPromptTemplate

from src.deps import get_llm, get_supabase
from src.state import BookState, ChapterSummary

logger = logging.getLogger(__name__)


chapter_prompt = ChatPromptTemplate.from_template(
    """
You are writing a book.

Book title: "{title}"

Full outline:
{outline}

You are now writing chapter number {chapter_number}.

Summaries of previous chapters:
{previous_summaries}

Editor notes for this chapter (if any):
{chapter_notes}

Write this chapter in clear, well-structured prose.
Length target: 1500-2500 words.

At the very end, add a short 3-5 sentence section starting with:
"Summary:"
that summarises this chapter.
"""
)


def _build_previous_summaries_text(state: BookState) -> str:
    if not state.chapter_summaries:
        return "No previous chapters (this is the first chapter)."
    return "\n\n".join(
        f"Chapter {cs.chapter_number} summary:\n{cs.summary}"
        for cs in state.chapter_summaries
    )


def generate_next_chapter(state: BookState) -> BookState:
    """
    Generate chapter N using previous summaries for context.
    Gating based on chapter_notes_status in Supabase.
    """
    supabase = get_supabase()

    n = state.current_chapter_number
    if n > state.total_chapters:
        logger.info(f"All {state.total_chapters} chapters completed")
        state.control["event"] = "all_chapters_done"
        return state

    logger.info(f"Generating Chapter {n}/{state.total_chapters}...")

    # Load existing chapter summaries from DB if state doesn't have them yet
    if not state.chapter_summaries and n > 1:
        try:
            resp = (
                supabase.table("chapter_summaries")
                .select("chapter_number, summary")
                .eq("book_id", state.book_id)
                .lt("chapter_number", n)
                # supabase-py versions differ; default is ascending if not specified
                .order("chapter_number")
                .execute()
            )
            if resp and hasattr(resp, 'data') and resp.data:
                state.chapter_summaries = [
                    ChapterSummary(chapter_number=row["chapter_number"], summary=row["summary"])
                    for row in resp.data
                ]
        except Exception:
            pass  # Continue with empty summaries if load fails

    # Load chapter gating + notes from Supabase
    # Note: chapter might not exist yet (first time generating), so use maybe_single()
    try:
        resp = (
            supabase.table("chapters")
            .select("editor_notes, chapter_notes_status")
            .eq("book_id", state.book_id)
            .eq("chapter_number", n)
            .maybe_single()
            .execute()
        )
        # Handle case where resp might be None or resp.data might be None
        if resp and hasattr(resp, 'data') and resp.data is not None:
            row = resp.data
        else:
            row = {}
    except Exception:
        row = {}
    
    chapter_notes_status = row.get("chapter_notes_status") if isinstance(row, dict) else None
    editor_notes = row.get("editor_notes") if isinstance(row, dict) else None

    if chapter_notes_status == "yes":
        logger.info(f"Chapter {n} waiting for editor notes")
        state.control["event"] = "waiting_for_chapter_notes"
        return state
    if chapter_notes_status not in (None, "no_notes_needed"):
        logger.warning(f"Chapter {n} paused - status: {chapter_notes_status}")
        state.control["event"] = "paused_for_chapter_notes_status"
        return state

    llm = get_llm()
    previous_summaries = _build_previous_summaries_text(state)
    if n > 1:
        logger.info(f"Using context from {len(state.chapter_summaries)} previous chapters")

    chain = chapter_prompt | llm
    logger.info(f"Calling LLM for Chapter {n}...")
    result = chain.invoke(
        {
            "title": state.title,
            "outline": state.outline,
            "chapter_number": n,
            "previous_summaries": previous_summaries,
            "chapter_notes": editor_notes or "",
        }
    )

    full_text = result.content.strip()
    summary = "Summary section not found."
    if "Summary:" in full_text:
        content_part, summary_part = full_text.split("Summary:", 1)
        full_text = content_part.strip()
        summary = summary_part.strip()

    # Save chapter
    supabase.table("chapters").upsert(
        {
            "book_id": state.book_id,
            "chapter_number": n,
            "title": f"Chapter {n}",
            "content": full_text,
            "status": "generated",
        }
    ).execute()

    # Save summary
    supabase.table("chapter_summaries").upsert(
        {
            "book_id": state.book_id,
            "chapter_number": n,
            "summary": summary,
        }
    ).execute()

    # Update state
    state.chapter_summaries.append(
        ChapterSummary(chapter_number=n, summary=summary)
    )
    state.current_chapter_number += 1
    logger.info(f"Chapter {n} generated and saved ({len(full_text)} chars)")
    state.control["event"] = "chapter_generated"
    return state

