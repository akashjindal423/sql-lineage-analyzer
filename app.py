import os
import google.generativeai as genai
from dotenv import load_dotenv
from sqllineage.runner import LineageRunner
from flask import Flask, render_template, request, jsonify, send_file

# Load API Key from .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if API key is missing
if gemini_api_key is None:
    print("""
    ❌ Error: Gemini API Key is missing. 
    
    Please set up your environment by:
    1. Creating a .env file in the project root
    2. Adding your Gemini API key like this: GEMINI_API_KEY=your_key_here
    
    You can get a Gemini API key from: https://aistudio.google.com/app/apikey
    """)
    # We'll continue without exiting, but AI functionality won't work
else:
    # Configure Gemini API
    genai.configure(api_key=gemini_api_key)
    print("✅ Gemini API configured successfully")

app = Flask(__name__)

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
    
    # Get all tables for network visualization
    all_tables = set()
    for s in sources:
        all_tables.add(s)
    for t in targets: 
        all_tables.add(t)
    for i in intermediates:
        all_tables.add(i)
    
    # Create links for visualization
    links = []
    
    # From source to intermediates
    for s in sources:
        for i in intermediates:
            links.append({"source": s, "target": i})
    
    # From intermediates to targets
    for i in intermediates:
        for t in targets:
            links.append({"source": i, "target": t})
    
    # Direct source to target if no intermediates
    if not intermediates:
        for s in sources:
            for t in targets:
                links.append({"source": s, "target": t})
    
    # Prepare data for visualization
    nodes = [{"id": table, "group": 1 if table in sources else (2 if table in targets else 3)} 
             for table in all_tables]
    
    return {
        "sources": sources,
        "targets": targets,
        "intermediates": intermediates,
        "nodes": nodes,
        "links": links
    }


def generate_explanation(sql_text, prompt):
    """Uses Gemini API to generate an explanation for the SQL query."""
    if gemini_api_key is None:
        return "⚠️ AI Explanation not available: Gemini API key not configured. Please add your API key to the .env file."
        
    try:
        # Try using version-specific model name
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
        response = model.generate_content(f"{prompt}\n\nSQL:\n{sql_text}")
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error with gemini-1.5-pro: {e}")
        try:
            # Fallback to another model
            model = genai.GenerativeModel(model_name="models/gemini-pro")
            response = model.generate_content(f"{prompt}\n\nSQL:\n{sql_text}")
            return response.text
        except Exception as e:
            print(f"❌ Gemini API Error with gemini-pro: {e}")
            return f"Error: Unable to generate explanation. Error: {str(e)}"


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', api_configured=(gemini_api_key is not None))


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze SQL and return lineage and explanation."""
    sql_text = request.form.get('sql_text', '')
    
    if not sql_text:
        return jsonify({"error": "No SQL provided"}), 400
    
    # Get lineage data and explanation
    lineage_data = analyze_lineage(sql_text)
    prompt = "Explain what this SQL query does in simple terms."
    explanation = generate_explanation(sql_text, prompt)
    
    # Combine results
    result = {
        "lineage": lineage_data,
        "explanation": explanation
    }
    
    return jsonify(result)


@app.route('/sql_examples/sql_lineage_test.sql')
def get_example_sql():
    """Serve the example SQL file."""
    return send_file('sql_examples/sql_lineage_test.sql')


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
