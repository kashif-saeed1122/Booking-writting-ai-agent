import logging

from langgraph.graph import StateGraph, END

from src.deps import get_supabase
from src.nodes.chapters import generate_next_chapter
from src.nodes.compile_book import compile_book
from src.nodes.notifications import notify
from src.nodes.outline import generate_outline
from src.state import BookState

logger = logging.getLogger(__name__)


def load_initial_state(book_id: str) -> BookState:
    """
    Load core fields for a book from Supabase and create BookState.
    """
    supabase = get_supabase()
    book = (
        supabase.table("books")
        .select(
            "id, title, notes_on_outline_before, outline, "
            "notes_on_outline_after, status_outline_notes, "
            "chapter_notes_status, final_review_notes_status, "
            "final_review_notes, book_output_status"
        )
        .eq("id", book_id)
        .single()
        .execute()
        .data
    )

    # Count total chapters already inferred or set (fallback to 0)
    # This can be pre-computed and stored in the books table if you like.
    total_chapters = book.get("total_chapters") or 0

    return BookState(
        book_id=book["id"],
        title=book["title"],
        notes_on_outline_before=book["notes_on_outline_before"],
        outline=book.get("outline"),
        notes_on_outline_after=book.get("notes_on_outline_after"),
        status_outline_notes=book.get("status_outline_notes"),
        chapter_notes_status=book.get("chapter_notes_status"),
        final_review_notes_status=book.get("final_review_notes_status"),
        final_review_notes=book.get("final_review_notes"),
        book_output_status=book.get("book_output_status"),
        total_chapters=total_chapters,
    )


def _router_after_outline(state: BookState) -> str:
    """
    Decide what to do after outline generation.
    """
    if state.control.get("event") == "missing_notes_on_outline_before":
        state.control["route_reason"] = "outline_missing_notes_before"
        return "notify"

    if state.control.get("event") != "outline_generated":
        return "notify"

    # Re-read outline gating status from DB
    supabase = get_supabase()
    book = (
        supabase.table("books")
        .select("status_outline_notes")
        .eq("id", state.book_id)
        .single()
        .execute()
        .data
    )
    status = book.get("status_outline_notes")
    state.status_outline_notes = status

    if status == "yes":
        logger.info("Outline approved, waiting for notes")
        state.control["event"] = "outline_waiting_for_notes"
        return "notify"
    if status == "no_notes_needed":
        logger.info("Outline approved, proceeding to chapter generation")
        return "generate_next_chapter"

    # 'no' or empty -> pause
    logger.warning(f"Outline paused - status: {status}")
    state.control["event"] = "outline_paused_missing_status"
    return "notify"


def _router_after_chapter(state: BookState) -> str:
    """
    Decide what to do after chapter generation.
    """
    event = state.control.get("event")
    if event in {
        "waiting_for_chapter_notes",
        "paused_for_chapter_notes_status",
    }:
        return "notify"

    if event == "chapter_generated":
        # If more chapters remain, keep generating
        if state.current_chapter_number <= state.total_chapters:
            return "generate_next_chapter"
        # All chapters done – move to compilation
        return "compile_book"

    if event == "all_chapters_done":
        return "compile_book"

    return "notify"


def _router_after_compile(state: BookState) -> str:
    """
    Decide what to do after compilation.
    """
    if state.control.get("event") == "book_compiled":
        return "notify"
    if state.control.get("event") == "final_review_not_ready":
        return "notify"
    return END


def build_graph():
    """
    Build and return the compiled LangGraph workflow.
    """
    workflow = StateGraph(BookState)

    workflow.add_node("generate_outline", generate_outline)
    workflow.add_node("generate_next_chapter", generate_next_chapter)
    workflow.add_node("compile_book", compile_book)
    workflow.add_node("notify", notify)

    workflow.set_entry_point("generate_outline")

    workflow.add_conditional_edges(
        "generate_outline",
        _router_after_outline,
        {
            "generate_next_chapter": "generate_next_chapter",
            "notify": "notify",
        },
    )

    workflow.add_conditional_edges(
        "generate_next_chapter",
        _router_after_chapter,
        {
            "generate_next_chapter": "generate_next_chapter",
            "compile_book": "compile_book",
            "notify": "notify",
        },
    )

    workflow.add_conditional_edges(
        "compile_book",
        _router_after_compile,
        {
            "notify": "notify",
            END: END,
        },
    )

    return workflow.compile()

