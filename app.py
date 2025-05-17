import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from shariah_audit_assistant import ShariahAuditAssistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize the assistant
PDF_FOLDER = os.getenv("PDF_FOLDER", "./pdfs")
try:
    assistant = ShariahAuditAssistant(pdf_folder=PDF_FOLDER)
    print(f"✅ Successfully initialized Shariah Audit Assistant with PDF folder: {PDF_FOLDER}")
except Exception as e:
    print(f"❌ Error initializing Shariah Audit Assistant: {e}")
    sys.exit(1)

@app.route('/')
def index():
    """
    Serve the main application page
    """
    return send_from_directory('static', 'index.html')

@app.route('/api/audit', methods=['POST'])
def audit_product():
    """
    API endpoint to audit a Shariah financial product
    """
    if not request.json or 'product_text' not in request.json:
        return jsonify({"error": "Missing product_text parameter"}), 400
   
    product_text = request.json['product_text']
   
    try:
        result = assistant.audit_product_description(product_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """
    API endpoint to extract structured data from a product description
    """
    if not request.json or 'product_text' not in request.json:
        return jsonify({"error": "Missing product_text parameter"}), 400
   
    product_text = request.json['product_text']
   
    try:
        result = assistant.extract_structured_data(product_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/check-clause', methods=['POST'])
def check_clause():
    """
    API endpoint to check if a specific clause is Shariah compliant
    """
    if not request.json or 'clause' not in request.json:
        return jsonify({"error": "Missing clause parameter"}), 400
   
    clause = request.json['clause']
   
    try:
        result = assistant.check_clause_compliance(clause)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    API endpoint to check if the service is running
    """
    return jsonify({"status": "healthy", "pdf_folder": PDF_FOLDER})

if __name__ == '__main__':
    # Make sure PDF folder exists
    os.makedirs(PDF_FOLDER, exist_ok=True)
   
    # Start the Flask app
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting Shariah Audit Assistant API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)