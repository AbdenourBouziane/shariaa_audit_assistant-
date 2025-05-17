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
USE_SEARCH = os.getenv("USE_SEARCH", "true").lower() == "true"

try:
    # Initialize without passing use_search parameter
    assistant = ShariahAuditAssistant(pdf_folder=PDF_FOLDER)
    print(f"✅ Successfully initialized Shariah Audit Assistant with PDF folder: {PDF_FOLDER}")
    print(f"🔍 External search functionality is {'enabled' if USE_SEARCH else 'disabled'}")
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
    use_search = request.json.get('use_search', USE_SEARCH)
    
    try:
        # Pass use_search as a parameter to the audit_product_description method if it accepts it
        # Otherwise, just use the global USE_SEARCH value in your backend logic
        result = assistant.audit_product_description(product_text)
        
        # If your assistant doesn't handle search internally, you can add search results here
        if use_search and USE_SEARCH and 'violations' in result:
            # This is a placeholder - implement according to your actual search functionality
            pass
            
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

@app.route('/api/search-standards', methods=['GET'])
def search_standards():
    """
    API endpoint to search for relevant Shariah standards
    """
    if not USE_SEARCH:
        return jsonify({"error": "Search functionality is disabled"}), 400
        
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400
    
    max_results = int(request.args.get('max_results', 3))
    
    try:
        # Implement a simple fallback if search_agent is not available
        if hasattr(assistant, 'search_agent') and assistant.search_agent:
            results = assistant.search_agent.search_standards(query, max_results)
        else:
            # Fallback to simulated results
            results = simulate_search_results(query, max_results)
            
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/standard-details', methods=['GET'])
def get_standard_details():
    """
    API endpoint to get detailed information about a specific Shariah standard
    """
    if not USE_SEARCH:
        return jsonify({"error": "Search functionality is disabled"}), 400
        
    reference = request.args.get('reference', '')
    if not reference:
        return jsonify({"error": "Missing reference parameter"}), 400
    
    try:
        # Check if get_standard_details is available in your assistant
        if hasattr(assistant, 'get_standard_details'):
            details = assistant.get_standard_details(reference)
            return jsonify(details)
        elif hasattr(assistant, 'search_agent') and hasattr(assistant.search_agent, 'get_detailed_standard'):
            details = assistant.search_agent.get_detailed_standard(reference)
            return jsonify(details)
        else:
            # Fallback to simulated results
            details = simulate_standard_details(reference)
            return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/find-source', methods=['POST'])
def find_source():
    """
    API endpoint to find source information for a clause
    """
    if not request.json or 'clause' not in request.json:
        return jsonify({"error": "Missing clause parameter"}), 400
    
    clause = request.json['clause']
    
    try:
        source_info = assistant.find_source_for_clause(clause)
        if source_info:
            return jsonify(source_info)
        else:
            return jsonify({"error": "No source found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/applicable-standards', methods=['GET'])
def get_applicable_standards():
    """
    API endpoint to get applicable Shariah standards for a product type
    """
    if not USE_SEARCH:
        return jsonify({"error": "Search functionality is disabled"}), 400
        
    product_type = request.args.get('product_type', '')
    if not product_type:
        return jsonify({"error": "Missing product_type parameter"}), 400
    
    try:
        # Check if get_applicable_standards is available in your assistant
        if hasattr(assistant, 'get_applicable_standards'):
            standards = assistant.get_applicable_standards(product_type)
            return jsonify({"standards": standards})
        elif hasattr(assistant, 'search_agent'):
            # Fallback to search_agent if available
            standards = assistant.search_agent.search_standards(product_type, 5)
            return jsonify({"standards": standards})
        else:
            # Fallback to simulated results
            standards = simulate_applicable_standards(product_type)
            return jsonify({"standards": standards})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    API endpoint to check if the service is running
    """
    return jsonify({
        "status": "healthy", 
        "pdf_folder": PDF_FOLDER,
        "search_enabled": USE_SEARCH
    })

# Helper functions for simulating search results when actual search is not available
def simulate_search_results(query, max_results=3):
    """Simulate search results for when actual search functionality is not available"""
    query = query.lower()
    
    # Basic dictionary of common Shariah finance concepts
    results = []
    
    if 'murabaha' in query:
        results.append({
            "title": "Murabaha (Cost-Plus Financing)",
            "snippet": "Murabaha is a sale contract where the seller explicitly declares the cost and profit margin. In Islamic banking, the bank purchases an asset and sells it to the client at a markup.",
            "source": "AAOIFI Shariah Standard No. 8"
        })
    
    if 'riba' in query or 'interest' in query:
        results.append({
            "title": "Prohibition of Riba (Interest)",
            "snippet": "Riba is strictly prohibited in Islamic finance. It refers to any excess compensation without due consideration. This includes interest on loans and investments.",
            "source": "AAOIFI Shariah Standard No. 21"
        })
    
    if 'gharar' in query or 'uncertainty' in query:
        results.append({
            "title": "Prohibition of Gharar (Uncertainty)",
            "snippet": "Gharar refers to excessive uncertainty or ambiguity in contracts. Islamic finance requires that all terms and conditions be clear, transparent and certain.",
            "source": "AAOIFI Shariah Standard No. 31"
        })
    
    if 'penalty' in query or 'default' in query:
        results.append({
            "title": "Late Payment Guidelines",
            "snippet": "Late payment penalties that generate profit for the lender are not permissible. However, penalties directed to charity may be allowed to discourage deliberate default.",
            "source": "AAOIFI Shariah Standard No. 3"
        })
    
    if 'bonds' in query or 'sukuk' in query:
        results.append({
            "title": "Sukuk (Islamic Bonds)",
            "snippet": "Conventional bonds are not Shariah-compliant due to their interest-based nature. Sukuk are the Islamic alternative, representing ownership in an underlying asset.",
            "source": "AAOIFI Shariah Standard No. 17"
        })
    
    # If no specific matches or not enough results, add general Islamic finance principles
    if len(results) < max_results:
        results.append({
            "title": "General Shariah Compliance Principles",
            "snippet": "Islamic finance prohibits interest (riba), excessive uncertainty (gharar), gambling (maysir), and investment in prohibited activities (haram).",
            "source": "General Shariah Principles"
        })
    
    return results[:max_results]

def simulate_standard_details(reference):
    """Simulate standard details for when actual functionality is not available"""
    standards_details = {
        "AAOIFI Shariah Standard No. 8": {
            "title": "Murabaha to the Purchase Orderer",
            "summary": "This standard defines the rules for Murabaha transactions where a client requests an institution to purchase an asset that the client promises to buy after the institution acquires it.",
            "key_requirements": [
                "The institution must actually own the asset before selling it",
                "There must be two separate contracts: purchase by institution and sale to client",
                "The sale price and profit margin must be clearly disclosed",
                "The asset must be lawful according to Shariah"
            ],
            "source": "Accounting and Auditing Organization for Islamic Financial Institutions"
        },
        "AAOIFI Shariah Standard No. 17": {
            "title": "Investment Sukuk",
            "summary": "This standard covers the rules for Sukuk (Islamic bonds) which represent common shares in the ownership of assets, usufruct, services, or certain projects.",
            "key_requirements": [
                "Sukuk must represent ownership in real assets, not debt",
                "Returns must be derived from the performance of the underlying assets",
                "Trading of Sukuk representing debt is restricted",
                "Sukuk structures must avoid interest-based elements"
            ],
            "source": "Accounting and Auditing Organization for Islamic Financial Institutions"
        }
    }
    
    # Try to find an exact match
    if reference in standards_details:
        return standards_details[reference]
    
    # Try to find a partial match
    for ref, details in standards_details.items():
        if reference.lower() in ref.lower():
            return details
    
    # Return a generic response if no match is found
    return {
        "title": "Standard Details",
        "summary": f"Detailed information for {reference} is not available in this simulation.",
        "key_requirements": ["Please refer to official AAOIFI documentation for accurate information."],
        "source": "Simulated Response"
    }

def simulate_applicable_standards(product_type):
    """Simulate applicable standards for a product type when actual functionality is not available"""
    product_type = product_type.lower()
    
    standards = []
    
    if 'murabaha' in product_type:
        standards.append({
            "title": "AAOIFI Shariah Standard No. 8: Murabaha",
            "summary": "Guidelines for Murabaha transactions in Islamic finance",
            "source": "AAOIFI"
        })
    
    if 'ijarah' in product_type or 'lease' in product_type:
        standards.append({
            "title": "AAOIFI Shariah Standard No. 9: Ijarah",
            "summary": "Guidelines for Ijarah (leasing) transactions in Islamic finance",
            "source": "AAOIFI"
        })
    
    if 'sukuk' in product_type or 'bond' in product_type:
        standards.append({
            "title": "AAOIFI Shariah Standard No. 17: Investment Sukuk",
            "summary": "Guidelines for Sukuk (Islamic bonds) in Islamic finance",
            "source": "AAOIFI"
        })
    
    if 'takaful' in product_type or 'insurance' in product_type:
        standards.append({
            "title": "AAOIFI Shariah Standard No. 26: Takaful",
            "summary": "Guidelines for Islamic insurance (Takaful) in Islamic finance",
            "source": "AAOIFI"
        })
    
    # Add general standards that apply to all Islamic financial products
    standards.append({
        "title": "AAOIFI Shariah Standard No. 21: Financial Papers",
        "summary": "General guidelines for financial instruments in Islamic finance",
        "source": "AAOIFI"
    })
    
    standards.append({
        "title": "AAOIFI Shariah Standard No. 1: Trading in Currencies",
        "summary": "Guidelines for currency exchange in Islamic finance",
        "source": "AAOIFI"
    })
    
    # For Islamic finance in general
    if 'islamic finance' in product_type or 'shariah' in product_type:
        standards.append({
            "title": "AAOIFI Conceptual Framework",
            "summary": "Foundational principles for Islamic financial products and services",
            "source": "AAOIFI"
        })
    
    return standards

if __name__ == '__main__':
    # Make sure PDF folder exists
    os.makedirs(PDF_FOLDER, exist_ok=True)
    
    # Start the Flask app
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting Shariah Audit Assistant API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
