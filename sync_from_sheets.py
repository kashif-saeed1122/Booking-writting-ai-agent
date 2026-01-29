"""
CLI script to sync Google Sheets to Supabase.
Run this before processing books, or schedule it to run periodically.
"""
import argparse
import logging
import sys

from src.sync_sheets import sync_sheet_to_supabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Google Sheets rows to Supabase books table."
    )
    parser.add_argument(
        "--sheet-id",
        help="Google Sheet ID (from URL). Can also set GOOGLE_SHEET_ID env var.",
    )
    parser.add_argument(
        "--worksheet",
        default="Sheet1",
        help="Worksheet name (default: Sheet1)",
    )
    args = parser.parse_args()

    import os

    sheet_id = args.sheet_id or os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        logger.error(
            "Sheet ID required. Use --sheet-id or set GOOGLE_SHEET_ID env var."
        )
        sys.exit(1)

    logger.info(f"Syncing sheet {sheet_id}...")
    book_ids = sync_sheet_to_supabase(sheet_id, worksheet_name=args.worksheet)
    logger.info(f"Synced {len(book_ids)} books. IDs: {book_ids}")


if __name__ == "__main__":
    main()
