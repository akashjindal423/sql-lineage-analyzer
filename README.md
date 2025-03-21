# SQL Lineage Analyzer with AI Explanation

A web-based tool that analyzes SQL queries to visualize table lineage and provides AI-generated explanations of SQL code.

![SQL Lineage Analyzer Screenshot](https://placeholder-for-screenshot.com/screenshot.png)

## Features

- **Visual SQL Lineage**: Generates an interactive network diagram showing the relationships between source, target, and intermediate tables in your SQL queries.
- **AI-Powered Explanations**: Uses Google's Gemini API to provide easy-to-understand explanations of what your SQL code does.
- **Interactive Web Interface**: Drag-and-drop visualization with color-coded nodes for better understanding.
- **Example SQL**: Comes with a pre-loaded example to demonstrate functionality.

## Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/sql-lineage-analyzer.git
cd sql-lineage-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

   > **Note**: You can get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey). The application will work without an API key, but AI explanations will not be available.

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open a web browser and go to:
```
http://localhost:5001
```

3. Enter your SQL code in the text area or click "Load Example" to try the built-in example.

4. Click "Analyze SQL" to generate the lineage diagram and AI explanation.

## Deployment

This application can be deployed to cloud platforms like Heroku, Render, or Google Cloud Run. Make sure to set the `GEMINI_API_KEY` as an environment variable in your deployment platform.

## How It Works

1. **SQL Parsing**: Uses the [sqllineage](https://github.com/reata/sqllineage) library to extract source and target tables from SQL code.
2. **Lineage Visualization**: Creates an interactive graph with D3.js to show relationships between tables.
3. **AI Explanation**: Sends the SQL to Google's Gemini API to generate a human-readable explanation.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [sqllineage](https://github.com/reata/sqllineage) for SQL parsing
- [D3.js](https://d3js.org/) for visualization
- [Google Gemini API](https://ai.google.dev/docs) for AI explanations
- [Flask](https://flask.palletsprojects.com/) for the web framework 