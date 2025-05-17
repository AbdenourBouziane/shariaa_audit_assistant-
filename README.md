# Shariah Audit Assistant - Deployment Guide

This guide will help you deploy the Shariah Audit Assistant application that consists of a Flask backend API and an HTML/CSS/JavaScript frontend.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Basic understanding of command line
- A directory to store PDF files for the system to analyze

## Project Structure

```
shariah-audit-assistant/
├── app.py                 # Flask API backend
├── shariah_audit_assistant.py  # Core logic code (your original code)
├── requirements.txt       # Python dependencies
├── static/               # Static files
│   └── index.html        # Frontend interface
├── pdfs/                 # Directory to store PDF files
└── README.md             # This file
```

## Step 1: Set Up the Environment

1. Create a new directory for your project:
   ```bash
   mkdir shariah-audit-assistant
   cd shariah-audit-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Create a `requirements.txt` file with the following content:
   ```
# Core LangChain components
langchain>=0.0.267
langchain-community>=0.0.9
langchain-together>=0.0.3

# LLM Provider
together>=0.1.5

# Vector Database
chromadb>=0.4.18

# Embedding models
sentence-transformers>=2.2.2

# PDF Processing
pypdf>=3.15.1

# API and Web Server
flask>=2.0.1
flask-cors>=3.0.10

# Environment and Configuration
python-dotenv>=1.0.0

# Utilities
tenacity>=8.2.2

# Optional: For better search performance
faiss-cpu>=1.7.4

# HuggingFace dependencies
transformers>=4.30.0
torch>=2.0.0

   ```

5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Create the Application Files

1. Save the `shariah_audit_assistant.py` file with your original code.

2. Create the Flask backend API (`app.py`), copying the code from the "app.py - Flask Backend API" artifact.

3. Create a directory for static files:
   ```bash
   mkdir -p static
   ```

4. Create the frontend interface (`static/index.html`), copying the code from the "index.html - Islamic Styled Frontend" artifact.

5. Create a directory for storing PDF files:
   ```bash
   mkdir -p pdfs
   ```

## Step 3: Configure Environment Variables

1. Create a `.env` file with your API key:
   ```
   TOGETHER_API_KEY=your_together_api_key
   PDF_FOLDER=./pdfs
   PORT=5000
   ```

   Replace `your_together_api_key` with your actual Together API key. If you don't have one, you'll need to sign up at https://together.ai

## Step 4: Run the Application

1. Make sure your virtual environment is activated.

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Your application should now be running at `http://localhost:5000`.

4. Open your browser and navigate to `http://localhost:5000/static/index.html` to access the frontend interface.

## Step 5: Using the Application

1. Upload your PDF documents to the `pdfs` directory.

2. The system will automatically analyze these documents and use them as a knowledge base.

3. Enter your financial product description or contract text in the input field.

4. Click "Perform Shariah Audit" to analyze the text.

5. View the results in the different tabs:
   - Summary: Overall compliance status and quick insights
   - Violations: Detailed list of non-compliant clauses
   - Detailed Analysis: In-depth analysis of all analyzed clauses

## Troubleshooting

- If you encounter any issues with the API, check the console output of the Flask application.
- Make sure your Together API key is correctly set in the `.env` file.
- If you face issues loading PDF files, verify that they are properly saved in the `pdfs` directory.

## Production Deployment

For production deployment, consider the following:

1. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

2. Consider using a reverse proxy like Nginx to serve static files and forward API requests to Gunicorn.

3. Deploy on a cloud platform like AWS, Google Cloud, or Azure, or use container services like Docker and Kubernetes.

4. Implement proper security measures, including HTTPS and API authentication.

## Customization

1. To change the theme colors, modify the CSS variables in the `:root` section of the HTML file.

2. To add more features, extend the Flask API and update the frontend accordingly.

3. For adding more analytical capabilities, enhance the `ShariahAuditAssistant` class in your core code file.
