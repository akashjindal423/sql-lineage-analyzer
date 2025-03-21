# lineage_renderer.py
from sqllineage.runner import LineageRunner

def get_lineage_details(sql_text):
    """Parses SQL and extracts source & target tables for lineage."""
    runner = LineageRunner(sql_text)

    sources = [str(tbl) for tbl in runner.source_tables]
    targets = [str(tbl) for tbl in runner.target_tables]

    edges = [(src, tgt) for src in sources for tgt in targets]

    return edges, sources, targets

def print_lineage_details(sql_text):
    """Prints lineage details in the terminal."""
    edges, sources, targets = get_lineage_details(sql_text)

    print("\n--- 📊 SQL Lineage ---")
    print(f"📥 Source Tables: {sources}")
    print(f"📤 Target Tables: {targets}")

    return edges, sources, targets

