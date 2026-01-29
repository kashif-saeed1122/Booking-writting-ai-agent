# Demo Quick Reference - One Page

## 🎯 5-Minute Demo Flow

### 1. **Show Excel Input** (30 sec)
```bash
# Show template
python create_excel_template.py
# Open books.xlsx - explain structure
```

### 2. **Sync to Database** (30 sec)
```bash
python sync_from_excel.py
# Show Supabase dashboard → books table
```

### 3. **Run Workflow** (2 min)
```bash
python worker.py --once
# Show logs in real-time:
# - Outline generation
# - Chapter generation (with context)
# - Compilation
# - File uploads
```

### 4. **Show Output** (1 min)
- Supabase Storage → Show .docx, .txt, .pdf files
- Download and open one file
- Show outline + chapters

### 5. **Show Visualization** (30 sec)
```bash
python visualize_graph.py
# Show graph.mmd or graph.png
# Explain LangGraph workflow
```

### 6. **Show Gating Logic** (30 sec)
- Supabase → Show status fields
- Explain: `yes` = wait, `no_notes_needed` = proceed
- Show notifications table

---

## 📋 Key Commands (In Order)

```bash
# 1. Create template
python create_excel_template.py

# 2. Edit books.xlsx (add your books)

# 3. Sync to database
python sync_from_excel.py

# 4. Process books
python worker.py --once

# 5. Visualize workflow
python visualize_graph.py

# 6. Test email (if needed)
python test_email.py
```

---

## 🎬 What to Say

**Opening:**
> "Automated book generation system using LangGraph. Takes Excel input, generates outlines and chapters with AI, compiles to Word/PDF/TXT."

**Key Points:**
- ✅ Modular LangGraph workflow
- ✅ Human-in-the-loop gating
- ✅ Context chaining (chapters use previous summaries)
- ✅ Simple Excel input
- ✅ Automatic processing

**Closing:**
> "Scalable, modular, supports human feedback at every stage. Ready for production use."

---

## 📊 Visualization Options

**Option 1: Mermaid Live Editor**
1. Run: `python visualize_graph.py`
2. Copy content from `graph.mmd`
3. Paste at: https://mermaid.live
4. Export as PNG/SVG

**Option 2: VS Code**
1. Install "Markdown Preview Mermaid Support" extension
2. Open `graph.mmd`
3. Right-click → Export as image

**Option 3: Command Line (if installed)**
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i graph.mmd -o graph.png
```

---

## ✅ Pre-Demo Checklist

- [ ] Excel file ready with 2-3 example books
- [ ] Supabase dashboard open
- [ ] Email/Teams ready (if showing notifications)
- [ ] Terminal ready with commands
- [ ] Visualization generated (`python visualize_graph.py`)
- [ ] One book pre-generated (for quick file viewing)

---

## 🎥 For Loom Video

**Structure:**
1. Intro (30s) - What it does
2. Excel input (1m) - Show template
3. Sync & DB (30s) - Show Supabase
4. Workflow (2m) - Run worker, show logs
5. Output (1m) - Show files
6. Visualization (30s) - Show graph
7. Summary (30s) - Key features

**Total: ~6 minutes**
