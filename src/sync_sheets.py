"""
Google Sheets sync module.
Reads rows from Google Sheets and upserts them into Supabase books table.
"""
import logging
import os
from typing import Dict, List, Optional

import gspread
from google.oauth2.service_account import Credentials

from src.deps import get_supabase

logger = logging.getLogger(__name__)


def get_sheets_client():
    """
    Initialize Google Sheets client using service account JSON.
    """
    service_account_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not service_account_file:
        raise ValueError(
            "GOOGLE_SERVICE_ACCOUNT_JSON env var not set. "
            "Point it to your service account JSON file."
        )

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(service_account_file, scopes=scope)
    return gspread.authorize(creds)


def sheet_row_to_book_dict(row_data: List, headers: List[str]) -> Optional[Dict]:
    """
    Convert a Google Sheets row (list of values) to a book dict
    using header mapping.
    """
    if len(row_data) < len(headers):
        # Pad with empty strings
        row_data = row_data + [""] * (len(headers) - len(row_data))

    book = {}
    for i, header in enumerate(headers):
        value = row_data[i] if i < len(row_data) else ""
        # Skip empty title (required field)
        if header == "title" and not value:
            return None
        book[header] = value.strip() if isinstance(value, str) else value

    return book


def sync_sheet_to_supabase(
    sheet_id: str,
    worksheet_name: str = "Sheet1",
    header_row: int = 1,
    start_row: int = 2,
) -> List[str]:
    """
    Sync Google Sheet rows to Supabase books table.

    Expected columns (case-insensitive):
    - title (required)
    - notes_on_outline_before (required)
    - status_outline_notes (yes/no/no_notes_needed)
    - notes_on_outline_after
    - chapter_notes_status (yes/no/no_notes_needed)
    - final_review_notes_status (yes/no/no_notes_needed)
    - final_review_notes
    - sheet_row_id (optional, for tracking)

    Returns list of book_ids that were created/updated.
    """
    client = get_sheets_client()
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)

    # Read headers
    headers_raw = worksheet.row_values(header_row)
    headers = [h.strip().lower().replace(" ", "_") for h in headers_raw]

    logger.info(f"Found columns: {headers}")

    # Read all data rows
    all_rows = worksheet.get_all_values()
    data_rows = all_rows[start_row - 1 :]  # Skip header row

    supabase = get_supabase()
    book_ids = []

    for idx, row_data in enumerate(data_rows, start=start_row):
        if not any(row_data):  # Skip completely empty rows
            continue

        book_dict = sheet_row_to_book_dict(row_data, headers)
        if not book_dict:
            logger.warning(f"Row {idx}: Skipping - missing title")
            continue

        title = book_dict.get("title")
        if not title:
            continue

        # Map sheet_row_id if present, otherwise use row number
        sheet_row_id = book_dict.get("sheet_row_id") or idx

        # Check if book already exists (by title or sheet_row_id)
        existing = (
            supabase.table("books")
            .select("id")
            .or_(f"title.eq.{title},sheet_row_id.eq.{sheet_row_id}")
            .maybe_single()
            .execute()
        )

        book_id = None
        if existing and existing.data:
            book_id = existing.data["id"]
            logger.info(f"Row {idx}: Updating existing book '{title}' ({book_id})")
        else:
            logger.info(f"Row {idx}: Creating new book '{title}'")

        # Prepare upsert payload (only include valid columns)
        upsert_data = {
            "title": title,
            "notes_on_outline_before": book_dict.get("notes_on_outline_before", ""),
            "sheet_row_id": sheet_row_id,
        }

        # Optional fields
        for field in [
            "notes_on_outline_after",
            "status_outline_notes",
            "chapter_notes_status",
            "final_review_notes_status",
            "final_review_notes",
        ]:
            if field in book_dict and book_dict[field]:
                upsert_data[field] = book_dict[field]

        # Set defaults if not provided
        if "status_outline_notes" not in upsert_data:
            upsert_data["status_outline_notes"] = "no_notes_needed"
        if "chapter_notes_status" not in upsert_data:
            upsert_data["chapter_notes_status"] = "no_notes_needed"
        if "final_review_notes_status" not in upsert_data:
            upsert_data["final_review_notes_status"] = "no_notes_needed"
        if "outline_status" not in upsert_data:
            upsert_data["outline_status"] = "pending"
        if "book_output_status" not in upsert_data:
            upsert_data["book_output_status"] = "not_started"

        if book_id:
            # Update existing
            supabase.table("books").update(upsert_data).eq("id", book_id).execute()
        else:
            # Insert new
            result = supabase.table("books").insert(upsert_data).execute()
            book_id = result.data[0]["id"] if result.data else None

        if book_id:
            book_ids.append(book_id)

    logger.info(f"Sync complete. Processed {len(book_ids)} books.")
    return book_ids


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    sheet_id = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("Usage: python -m src.sync_sheets <SHEET_ID>")
        print("Or set GOOGLE_SHEET_ID env var")
        sys.exit(1)

    sync_sheet_to_supabase(sheet_id)
