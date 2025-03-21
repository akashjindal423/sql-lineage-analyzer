import os
import google.generativeai as genai
from dotenv import load_dotenv
from sqllineage.runner import LineageRunner

# Load API Key from .env file
load_dotenv()
print("DEBUG - .env loaded")
print("DEBUG - Retrieved key:", os.getenv("GEMINI_API_KEY"))
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if API key is missing
if gemini_api_key is None:
    print("❌ Error: Gemini API Key is missing. Make sure it's set in the .env file.")
    exit(1)

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

# Print available models
print("Available models:")
try:
    for m in genai.list_models():
        print(f"- {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Hardcoded SQL file path (inside sql_examples folder)
SQL_FILE_PATH = "sql_examples/sql_lineage_test.sql"

def read_sql_file(file_path):
    """Reads and returns the content of a SQL file."""
    if not os.path.exists(file_path):
        print(f"❌ Error: SQL file not found at {file_path}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"❌ Error reading SQL file: {e}")
        return None

def analyze_lineage(sql_text):
    """Parses SQL and returns source & target tables with proper categorization."""
    runner = LineageRunner(sql_text)
    
    # Extract statements that actually modify data
    create_statements = []
    insert_statements = []
    select_statements = []
    
    for stmt in sql_text.split(';'):
        stmt = stmt.strip().upper()
        if stmt.startswith('CREATE'):
            create_statements.append(stmt)
        elif stmt.startswith('INSERT'):
            insert_statements.append(stmt)
        elif stmt.startswith('SELECT'):
            select_statements.append(stmt)
    
    # Created tables are targets
    create_tables = set()
    for stmt in create_statements:
        if 'CREATE TABLE' in stmt or 'CREATE VIEW' in stmt:
            # Extract table name after CREATE TABLE or CREATE VIEW
            parts = stmt.split()
            if len(parts) >= 3:  # CREATE TABLE/VIEW name
                table_name = parts[2].strip()
                # Remove any parentheses or additional qualifiers
                table_name = table_name.split('(')[0].strip()
                create_tables.add(f"<default>.{table_name}")
    
    # Tables used in SELECT but not in CREATE are true sources
    sources_set = set()
    for table in runner.source_tables:
        table_str = str(table)
        if table_str not in create_tables:
            sources_set.add(table_str)
    
    # Tables in CREATE statements are targets
    targets_set = set()
    for table in create_tables:
        targets_set.add(table)
    
    # Tables in both CREATE and SELECT are intermediates
    intermediate_tables = set()
    for table in runner.source_tables:
        table_str = str(table)
        if table_str in create_tables:
            intermediate_tables.add(table_str)
    
    # Format for display
    sources = [table.replace("Table: ", "") for table in sources_set]
    targets = [table.replace("Table: ", "") for table in targets_set]
    intermediates = [table.replace("Table: ", "") for table in intermediate_tables]
    
    # If our analysis fails to identify proper sources/targets, fall back to the original
    if not sources and not targets:
        print("Using fallback lineage analysis")
        sources = [str(table).replace("Table: ", "") for table in runner.source_tables]
        targets = [str(table).replace("Table: ", "") for table in runner.target_tables]
    
    return sources, targets, intermediates


def generate_explanation(sql_text, prompt):
    """Uses Gemini API to generate an explanation for the SQL query."""
    try:
        # Try using version-specific model name
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        print("Using model: models/gemini-1.5-pro")
        response = model.generate_content(f"{prompt}\n\nSQL:\n{sql_text}")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error with gemini-1.5-pro: {e}")
        try:
            # Fallback to another model
            model = genai.GenerativeModel(model_name="models/gemini-pro")
            print("Using model: models/gemini-pro")
            response = model.generate_content(f"{prompt}\n\nSQL:\n{sql_text}")
            return response.text
        except Exception as e:
            print(f"❌ Gemini API Error with gemini-pro: {e}")
            return "Error: Unable to generate explanation."


def main():
    """Main function to run SQL lineage analysis and AI-generated explanation."""
    print(f"📂 Using SQL file: {SQL_FILE_PATH}")

    sql_text = read_sql_file(SQL_FILE_PATH)
    if sql_text is None:
        return  # Stop execution if file is missing

    sources, targets, intermediates = analyze_lineage(sql_text)

    print("\n--- 📊 SQL Lineage ---")
    print(f"📥 Source Tables: {sources}")
    print(f"📤 Target Tables: {targets}")
    print(f"🔄 Intermediate Tables: {intermediates}")

    prompt = "Explain what this SQL query does in simple terms."
    explanation = generate_explanation(sql_text, prompt)

    print("\n--- 🤖 AI Explanation ---")
    print(explanation)

    output_file = SQL_FILE_PATH.replace(".sql", "_analysis.txt")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("📊 SQL Lineage\n")
            f.write(f"Source Tables: {sources}\n")
            f.write(f"Target Tables: {targets}\n")
            f.write(f"Intermediate Tables: {intermediates}\n\n")
            f.write("🤖 AI Explanation:\n")
            f.write(explanation)
        print(f"✅ Output saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving output file: {e}")

if __name__ == "__main__":
    main()
