"""
LangGraph Visualization Tool

Generates Mermaid diagram and/or PNG image of the LangGraph workflow.

USAGE:
    python visualize_graph.py
    
    This will:
    1. Generate graph.mmd (Mermaid diagram)
    2. Generate graph.png (if graphviz is installed)
    3. Print Mermaid code to console

WHAT IT DOES:
    - Visualizes the LangGraph state machine
    - Shows nodes (outline, chapters, compile, notify)
    - Shows conditional edges and routing logic
    - Creates visual representation for demos/documentation

END GOAL:
    - Show the workflow architecture visually
    - Use in presentations/demos
    - Document the system design
"""
import logging
from pathlib import Path

from src.graph import build_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mermaid_diagram() -> str:
    """
    Generate Mermaid diagram code for the LangGraph workflow.
    """
    mermaid = """graph TD
    Start([Start]) --> GenerateOutline[Generate Outline]
    
    GenerateOutline -->|Outline Generated| CheckOutlineStatus{Check Outline Status}
    GenerateOutline -->|Missing Notes| Notify1[Notify: Missing Notes]
    
    CheckOutlineStatus -->|status = yes| Notify2[Notify: Waiting for Notes]
    CheckOutlineStatus -->|status = no_notes_needed| GenerateChapter[Generate Next Chapter]
    CheckOutlineStatus -->|status = no/empty| Notify3[Notify: Paused]
    
    GenerateChapter -->|Chapter Generated| CheckMoreChapters{More Chapters?}
    GenerateChapter -->|Waiting for Notes| Notify4[Notify: Waiting for Chapter Notes]
    GenerateChapter -->|Paused| Notify5[Notify: Paused]
    
    CheckMoreChapters -->|Yes| GenerateChapter
    CheckMoreChapters -->|No| CompileBook[Compile Book]
    
    CompileBook -->|Compiled| Notify6[Notify: Book Compiled]
    CompileBook -->|Not Ready| Notify7[Notify: Final Review Not Ready]
    
    Notify1 --> End([End])
    Notify2 --> End
    Notify3 --> End
    Notify4 --> End
    Notify5 --> End
    Notify6 --> End
    Notify7 --> End
    
    style GenerateOutline fill:#e1f5ff
    style GenerateChapter fill:#e1f5ff
    style CompileBook fill:#e1f5ff
    style Notify1 fill:#fff4e1
    style Notify2 fill:#fff4e1
    style Notify3 fill:#fff4e1
    style Notify4 fill:#fff4e1
    style Notify5 fill:#fff4e1
    style Notify6 fill:#d4edda
    style Notify7 fill:#fff4e1
    style Start fill:#d1ecf1
    style End fill:#d1ecf1
"""
    return mermaid


def save_mermaid_file(content: str, filename: str = "graph.mmd"):
    """Save Mermaid diagram to file."""
    Path(filename).write_text(content, encoding="utf-8")
    logger.info(f"✓ Saved Mermaid diagram: {filename}")
    logger.info(f"  View at: https://mermaid.live (paste content)")
    logger.info(f"  Or use: VS Code Mermaid extension, GitHub, etc.")


def generate_detailed_mermaid() -> str:
    """
    Generate a more detailed Mermaid diagram with state information.
    """
    mermaid = """graph TB
    subgraph "Input Stage"
        Excel[Excel File<br/>books.xlsx]
        Sync[Sync Script<br/>sync_from_excel.py]
        DB[(Supabase DB<br/>books table)]
    end
    
    subgraph "LangGraph Workflow"
        Start([Start]) --> LoadState[Load Book State<br/>from Supabase]
        
        LoadState --> GenerateOutline[Generate Outline<br/>Using LLM]
        
        GenerateOutline --> CheckOutline{Outline<br/>Status?}
        CheckOutline -->|yes| WaitOutline[Wait for<br/>Editor Notes]
        CheckOutline -->|no_notes_needed| GenerateChapter[Generate Chapter N<br/>Using Previous Summaries]
        CheckOutline -->|no/empty| PauseOutline[Pause]
        
        GenerateChapter --> CheckChapter{Chapter<br/>Status?}
        CheckChapter -->|yes| WaitChapter[Wait for<br/>Chapter Notes]
        CheckChapter -->|no_notes_needed| MoreChapters{More<br/>Chapters?}
        CheckChapter -->|no/empty| PauseChapter[Pause]
        
        MoreChapters -->|Yes| GenerateChapter
        MoreChapters -->|No| CompileBook[Compile Book<br/>DOCX + TXT + PDF]
        
        CompileBook --> CheckFinal{Final Review<br/>Ready?}
        CheckFinal -->|Yes| UploadFiles[Upload to<br/>Supabase Storage]
        CheckFinal -->|No| WaitFinal[Wait for<br/>Final Notes]
        
        UploadFiles --> Notify[Send Notifications<br/>Email + Teams]
        Notify --> End([End])
        
        WaitOutline --> Notify
        WaitChapter --> Notify
        WaitFinal --> Notify
        PauseOutline --> Notify
        PauseChapter --> Notify
    end
    
    subgraph "Output Stage"
        Storage[(Supabase Storage<br/>books-output bucket)]
        Files[Generated Files<br/>.docx .txt .pdf]
    end
    
    Excel --> Sync
    Sync --> DB
    DB --> LoadState
    UploadFiles --> Storage
    Storage --> Files
    
    style GenerateOutline fill:#e1f5ff
    style GenerateChapter fill:#e1f5ff
    style CompileBook fill:#e1f5ff
    style UploadFiles fill:#d4edda
    style Notify fill:#fff4e1
    style Start fill:#d1ecf1
    style End fill:#d1ecf1
"""
    return mermaid


def try_generate_png(mermaid_content: str, output_file: str = "graph.png"):
    """
    Try to generate PNG from Mermaid using mermaid-cli or graphviz.
    Falls back gracefully if tools aren't installed.
    """
    try:
        # Try mermaid-cli (mmdc)
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_content)
            temp_mmd = f.name

        try:
            result = subprocess.run(
                ["mmdc", "-i", temp_mmd, "-o", output_file, "-b", "transparent"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info(f"✓ Generated PNG: {output_file}")
                Path(temp_mmd).unlink()
                return True
        except FileNotFoundError:
            pass

        Path(temp_mmd).unlink()

    except Exception as e:
        logger.debug(f"PNG generation skipped: {e}")

    # Fallback: Instructions
    logger.info("")
    logger.info("To generate PNG image:")
    logger.info("  1. Install: npm install -g @mermaid-js/mermaid-cli")
    logger.info("  2. Run: mmdc -i graph.mmd -o graph.png")
    logger.info("  OR paste graph.mmd content at: https://mermaid.live")
    return False


def main():
    """Generate visualization files."""
    logger.info("Generating LangGraph visualization...")

    # Generate simple diagram
    simple_mermaid = generate_mermaid_diagram()
    save_mermaid_file(simple_mermaid, "graph.mmd")

    # Generate detailed diagram
    detailed_mermaid = generate_detailed_mermaid()
    save_mermaid_file(detailed_mermaid, "graph_detailed.mmd")

    # Try to generate PNG
    try_generate_png(simple_mermaid, "graph.png")
    try_generate_png(detailed_mermaid, "graph_detailed.png")

    # Print to console
    print("\n" + "=" * 60)
    print("MERMAID DIAGRAM CODE")
    print("=" * 60)
    print("\nSimple version (graph.mmd):")
    print(simple_mermaid)
    print("\n" + "=" * 60)
    print("\nDetailed version (graph_detailed.mmd):")
    print(detailed_mermaid)
    print("\n" + "=" * 60)

    logger.info("\n✓ Visualization files generated!")
    logger.info("\nNext steps:")
    logger.info("  - View graph.mmd at: https://mermaid.live")
    logger.info("  - Use in VS Code with Mermaid extension")
    logger.info("  - Include in README.md or documentation")
    logger.info("  - Use in presentations/demos")


if __name__ == "__main__":
    main()
