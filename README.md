## Automated Book Generation System (LangGraph + Supabase)

This project is a minimal but working implementation of the book-generation flow built with **LangGraph + LangChain**, **Supabase**, and **OpenAI**.

It supports:

- Outline generation with gating on `notes_on_outline_before` and `status_outline_notes`.
- Chapter-by-chapter generation with previous-chapter summaries as context.
- Final compilation to `.docx` (and text in-memory), saved to **Supabase Storage**.
- Notification hooks for **email** (SMTP).

### 1. Tech stack

- **Language / Orchestration**: Python, LangGraph, LangChain
- **LLM**: OpenAI (GPT-4.1 / 4.1-mini, configurable via env)
- **Database**: Supabase (Postgres)
- **Storage**: Supabase Storage bucket `books-output`
- **Notifications**: SMTP email
---

### 2. Supabase setup

1. Create a new Supabase project.
2. In the SQL editor, run the schema from the prompt/spec (tables: `books`, `chapters`, `chapter_summaries`, `notifications`, etc.).
3. Create a **Storage bucket** named `books-output` and make it public, or configure RLS/public URLs as you prefer.
4. Copy:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

You must insert at least one row into `books` manually to test:

- `id`: UUID (keep it for later).
- `title`: your book title.
- `notes_on_outline_before`: some non-empty text.
- `status_outline_notes`: `no_notes_needed` (to auto-proceed).
- `chapter_notes_status`: `no_notes_needed`.
- `final_review_notes_status`: `no_notes_needed`.

> For a very first test, you don't need any rows in `chapters` – the system will create/overwrite them.

---

### 3. Environment configuration

1. Copy `.env.example` to `.env`:

```bash
cd d:/codeaza_workspace/task
copy .env.example .env
```

2. Edit `.env` and fill in:

- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- SMTP + email settings (optional; if you leave them blank, notifications become no-ops).
- `TEAMS_WEBHOOK_URL` (optional; blank means no-op).

---

### 4. Install dependencies

In PowerShell, from the project root:

```bash
cd d:/codeaza_workspace/task
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Make sure `python` points to Python 3.10+.

---

### 5. Run a book flow

1. Get the `id` of a `books` row you created in Supabase (copy the UUID).
2. From the virtual environment in the project root:

```bash
python run_book_flow.py --book-id YOUR_BOOK_UUID
```

The script will:

- Load the book state.
- Generate an outline (respecting `notes_on_outline_before` and `status_outline_notes`).
- Generate chapters, chaining summaries.
- Attempt to compile the final book if final review gating passes.
- Upload the `.docx` file to Supabase Storage and set `output_file_url` on the `books` row.

You should see in the console:

- `Flow finished.`
- A final event (e.g. `book_compiled` or `final_review_not_ready`).
- The final `book_output_status` (e.g. `ready`).

---





