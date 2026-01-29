# Demo Script - Step-by-Step Presentation Guide

## 🎯 Demo Flow (5-10 minutes)

### **Part 1: Introduction (1 min)**
**What to say:**
> "I've built an automated book generation system using LangGraph, LangChain, Supabase, and OpenAI. It takes a book title and instructions, generates an outline, writes chapters with context chaining, and compiles everything into Word, PDF, and text files."

---

### **Part 2: Show the Architecture (1 min)**

**Show:**
- Excel file → Sync → Supabase DB → LangGraph Workflow → Output Files
- Mention: LangGraph handles the state machine, gating logic, and human-in-the-loop

**Visual:**
```bash
# Show the LangGraph visualization
python visualize_graph.py
# Opens graph.png or shows Mermaid diagram
```

---

### **Part 3: Excel Input (1 min)**

**What to say:**
> "Editors can manage books in a simple Excel file - no complex setup needed."

**Commands:**
```bash
# 1. Show how to create template
python create_excel_template.py

# 2. Open books.xlsx (show the structure)
# Explain: title, notes_on_outline_before, status fields

# 3. Show your actual Excel file with real books
```

**What to explain:**
- Row 1: Headers (blue)
- Row 2: Descriptions (gray, for reference)
- Row 3+: Actual book data
- Required fields: `title`, `notes_on_outline_before`
- Status fields control the workflow gates

---

### **Part 4: Sync to Database (1 min)**

**What to say:**
> "We sync the Excel data to Supabase, which acts as our single source of truth."

**Commands:**
```bash
# Sync Excel to Supabase
python sync_from_excel.py
```

**Show:**
- Console output showing books being created/updated
- Supabase dashboard → `books` table → Show the rows
- Explain: Each book gets a UUID, status fields control workflow

---

### **Part 5: Run the Workflow (2-3 min)**

**What to say:**
> "Now let's process the books through our LangGraph workflow. It will generate outlines, chapters with context chaining, and compile everything."

**Commands:**
```bash
# Option A: Process all books automatically
python worker.py --once

# Option B: Process one book manually (for detailed demo)
python run_book_flow.py --book-id YOUR_BOOK_UUID
```

**What to show:**
- **Logs in real-time:**
  - "Generating outline..."
  - "Outline generated. Detected 5 chapters"
  - "Generating Chapter 1/5..."
  - "Using context from 1 previous chapters"
  - "Chapter 1 generated and saved"
  - ... (repeat for each chapter)
  - "Compiling final book..."
  - "Found 5 chapters to compile"
  - "Uploading ...docx to Supabase Storage..."
  - "Book compilation complete!"

- **Supabase Dashboard:**
  - `books` table → Show `outline` field filled
  - `chapters` table → Show all chapters generated
  - `chapter_summaries` table → Show context chaining
  - `books.output_file_url` → Show link to files

---

### **Part 6: Show Output Files (1 min)**

**What to say:**
> "The system generates three formats: Word document, PDF, and plain text - all stored in Supabase Storage."

**Show:**
- Supabase Storage → `books-output` bucket
- Show files: `{book_id}.docx`, `{book_id}.txt`, `{book_id}.pdf`
- Download and open one file to show content
- Show the outline, chapters, proper formatting

---

### **Part 7: Show Gating Logic (1 min)**

**What to say:**
> "The system supports human-in-the-loop with gating logic at every stage."

**Show in Supabase:**
- `books.status_outline_notes` = `yes` → System waits for editor notes
- `books.chapter_notes_status` = `yes` → System waits before generating chapters
- `books.final_review_notes_status` = `no_notes_needed` → Auto-proceeds

**Explain:**
- Editor can add notes → System regenerates with feedback
- Status fields control workflow flow
- Notifications sent at key points

---

### **Part 8: Show Notifications (30 sec)**

**What to say:**
> "The system sends email and MS Teams notifications at key events."

**Show:**
- Email inbox → Show notification emails
- MS Teams channel → Show webhook messages
- `notifications` table in Supabase → Show notification log

---

### **Part 9: LangGraph Visualization (1 min)**

**What to say:**
> "Here's the LangGraph workflow that orchestrates everything."

**Commands:**
```bash
python visualize_graph.py
```

**Show:**
- Mermaid diagram or PNG image
- Explain nodes: `generate_outline`, `generate_next_chapter`, `compile_book`, `notify`
- Explain conditional edges and routing logic
- Show state transitions

---

### **Part 10: Summary & Q&A (1 min)**

**Key Points to Emphasize:**
1. ✅ **Modular design** - Each stage is a separate node
2. ✅ **Human-in-the-loop** - Gating logic at every stage
3. ✅ **Context chaining** - Chapters use previous summaries
4. ✅ **Scalable** - Can process many books automatically
5. ✅ **Simple input** - Just Excel file, no complex setup

**Tech Stack:**
- LangGraph + LangChain (orchestration)
- OpenAI GPT-4 (content generation)
- Supabase (database + storage)
- Excel (input, no auth needed)
- Email/Teams (notifications)

---

## 📋 Quick Command Reference

```bash
# 1. Create Excel template
python create_excel_template.py

# 2. Edit books.xlsx (add your books)

# 3. Sync to database
python sync_from_excel.py

# 4. Process books
python worker.py --once

# 5. Visualize workflow
python visualize_graph.py

# 6. Test email
python test_email.py
```

---

## 🎬 Pro Tips for Demo

1. **Have everything ready:**
   - Excel file with 2-3 example books
   - Supabase dashboard open
   - Email/Teams ready to show notifications

2. **Run commands live** - Shows it's working, not pre-recorded

3. **Explain the "why"** - Not just what it does, but why each design choice

4. **Show errors gracefully** - If something fails, show how logging helps debug

5. **Emphasize simplicity** - Excel input, automatic processing, simple setup

6. **Time management:**
   - Fast parts: Excel sync, file viewing
   - Slow parts: Chapter generation (show logs, explain it's working)
   - Skip: Waiting for full book generation (use pre-generated example)

---

## 🎥 For Loom Video

**Suggested structure:**
1. Intro (30 sec) - What the system does
2. Architecture diagram (30 sec) - Show LangGraph visualization
3. Excel input (1 min) - Show template, explain structure
4. Sync & Database (1 min) - Show Supabase tables
5. Workflow execution (2 min) - Run worker, show logs
6. Output files (1 min) - Show generated files
7. Gating logic (1 min) - Show status fields, explain workflow control
8. Summary (30 sec) - Key features, tech stack

**Total: ~7-8 minutes**
