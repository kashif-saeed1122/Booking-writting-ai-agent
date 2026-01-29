import argparse
import logging
import sys

from src.sync_excel import sync_excel_to_supabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Excel (.xlsx) rows to Supabase books table."
    )
    parser.add_argument(
        "--file",
        default="books.xlsx",
        help="Path to Excel file (default: books.xlsx)",
    )
    parser.add_argument(
        "--worksheet",
        default="Sheet1",
        help="Worksheet name (default: Sheet1)",
    )
    args = parser.parse_args()

    logger.info(f"Syncing Excel file: {args.file}")
    try:
        book_ids = sync_excel_to_supabase(args.file, worksheet_name=args.worksheet)
        logger.info(f"✓ Synced {len(book_ids)} books. IDs: {book_ids}")
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
