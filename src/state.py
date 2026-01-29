from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class ChapterSummary(BaseModel):
    chapter_number: int
    summary: str


class BookState(BaseModel):
    """
    LangGraph state for a single book run.
    This is hydrated from Supabase at the start of a run.
    """

    book_id: str
    title: str
    notes_on_outline_before: str

    outline: Optional[str] = None
    notes_on_outline_after: Optional[str] = None
    status_outline_notes: Optional[str] = None

    current_chapter_number: int = 1
    total_chapters: int = 0
    chapter_notes_status: Optional[str] = None
    chapter_notes: Optional[str] = None
    chapter_summaries: List[ChapterSummary] = []

    final_review_notes_status: Optional[str] = None
    final_review_notes: Optional[str] = None
    book_output_status: Optional[str] = None

    # Generic control/event info for routing
    control: Dict[str, Any] = {}

