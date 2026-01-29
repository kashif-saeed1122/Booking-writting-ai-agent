import logging
import time
from typing import List, Optional

from src.deps import get_supabase
from src.graph import build_graph, load_initial_state
from src.state import BookState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def find_pending_books(limit: int = 10) -> List[str]:
    """
    Find books that are ready to be processed:
    - outline_status = 'pending' (need outline)
    - outline_status = 'approved' and chapters not started
    - chapters in progress but next chapter ready
    - all chapters done but not compiled
    """
    supabase = get_supabase()

    # Find books needing outline generation
    pending_outline = (
        supabase.table("books")
        .select("id")
        .eq("outline_status", "pending")
        .not_.is_("notes_on_outline_before", "null")
        .limit(limit)
        .execute()
    )

    book_ids = [row["id"] for row in (pending_outline.data or [])]

    # Find books with approved outline but no chapters started
    approved_outline = (
        supabase.table("books")
        .select("id")
        .eq("outline_status", "approved")
        .eq("book_output_status", "not_started")
        .limit(limit)
        .execute()
    )

    book_ids.extend([row["id"] for row in (approved_outline.data or [])])

    # Find books with chapters in progress
    # (simplified: just check if outline is approved and status allows)
    in_progress = (
        supabase.table("books")
        .select("id")
        .eq("outline_status", "approved")
        .in_("book_output_status", ["not_started", "in_progress"])
        .limit(limit)
        .execute()
    )

    book_ids.extend([row["id"] for row in (in_progress.data or [])])

    # Deduplicate
    return list(set(book_ids))


def process_book(book_id: str) -> bool:
    """
    Process a single book through the workflow.
    Returns True if successful, False if error or paused.
    """
    try:
        logger.info(f"Processing book_id: {book_id}")
        workflow = build_graph()
        state = load_initial_state(book_id)

        final_state = workflow.invoke(state)
        # Ensure final_state is a BookState instance (some runtimes return dict)
        if isinstance(final_state, dict):
            final_state = BookState.parse_obj(final_state)

        event = final_state.control.get("event")
        if event == "book_compiled":
            logger.info(f"✓ Book {book_id} completed successfully")
            return True
        elif event in ["waiting_for_chapter_notes", "outline_waiting_for_notes"]:
            logger.info(f"⏸ Book {book_id} paused - waiting for editor input")
            return False
        else:
            logger.info(f"⏸ Book {book_id} paused - event: {event}")
            return False

    except Exception as e:
        logger.error(f"✗ Error processing book {book_id}: {e}", exc_info=True)
        # Mark book as error in DB
        try:
            supabase = get_supabase()
            supabase.table("books").update(
                {"book_output_status": "error"}
            ).eq("id", book_id).execute()
        except Exception:
            pass
        return False


def run_worker_once(limit: int = 5, book_ids: Optional[List[str]] = None):
    """
    Run one iteration of the worker: find pending books and process them.
    
    Args:
        limit: How many pending books to process (if book_ids not provided)
        book_ids: Specific book IDs to process (if provided, ignores limit)
    """
    if book_ids:
        pending = book_ids
        logger.info(f"Worker: Processing {len(pending)} provided book_id(s)")
    else:
        logger.info("Worker: Checking for pending books...")
        pending = find_pending_books(limit=limit)

    if not pending:
        logger.info("No pending books found.")
        return

    logger.info(f"Found {len(pending)} pending book(s)")
    for book_id in pending:
        process_book(book_id)
        # Small delay between books
        time.sleep(2)


def run_worker_loop(interval_seconds: int = 60):
    """
    Run worker in a loop, checking every interval_seconds.
    """
    logger.info(f"Starting worker loop (checking every {interval_seconds}s)")
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            run_worker_once()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated worker for book generation system."
    )
    parser.add_argument(
        "--book-id",
        action="append",
        dest="book_ids",
        help="Process a specific book UUID. Can be provided multiple times.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for cron/n8n)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="How many pending books to process when using --once (default: 5)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Polling interval in seconds (default: 60)",
    )

    args = parser.parse_args()

    # If book-id is provided, process those directly
    if args.book_ids:
        run_worker_once(book_ids=args.book_ids)
    elif args.once:
        run_worker_once(limit=args.limit)
    else:
        run_worker_loop(interval_seconds=args.interval)
