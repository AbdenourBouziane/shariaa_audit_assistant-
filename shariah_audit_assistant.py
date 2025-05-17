import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_together import Together
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Load environment variables from .env if present
load_dotenv()

# Set API key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "e5126de3e93510fc8f8cac65e28c9351a54ee255d72a0c26ae612794bcf9f0bc")
os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(ValueError)
)
def safe_invoke(llm, prompt: str):
    return llm.invoke(prompt)

class ShariahAuditAssistant:
    def __init__(self, pdf_folder: str):
        self.pdf_folder = pdf_folder
        self.llm = Together(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0.0,
            max_tokens=1024,
            together_api_key=TOGETHER_API_KEY
        )
        self.vector_db = self._create_vector_db()

    def _create_vector_db(self) -> Chroma:
        pdf_files = [os.path.join(self.pdf_folder, f) for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        all_docs = []

        for file in pdf_files:
            try:
                loader = PyPDFLoader(file)
                docs = loader.load()
                for doc in docs:
                    doc.metadata['source'] = os.path.basename(file)
                all_docs.extend(docs)
                print(f"✅ Loaded {len(docs)} pages from {os.path.basename(file)}")
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")

        # If no PDFs are found or loaded, create a minimal document set
        if not all_docs:
            print("⚠️ No PDF documents found. Creating a minimal default database.")
            from langchain_core.documents import Document
            # Create basic Shariah finance principles document
            all_docs = [
                Document(
                    page_content="Riba (interest) is prohibited in Islamic finance. Any contractual increase over the principal in a loan is considered riba.",
                    metadata={"source": "default_principles.pdf"}
                ),
                Document(
                    page_content="Gharar (excessive uncertainty) should be avoided in Islamic contracts. Terms should be clear and well-defined.",
                    metadata={"source": "default_principles.pdf"}
                ),
                Document(
                    page_content="Maysir (gambling/speculation) is prohibited in Islamic finance. Contracts should be based on real economic activities.",
                    metadata={"source": "default_principles.pdf"}
                ),
                Document(
                    page_content="Investment in haram (prohibited) activities is not allowed, such as alcohol, pork products, conventional banking, or weapons.",
                    metadata={"source": "default_principles.pdf"}
                ),
                Document(
                    page_content="Murabaha is a cost-plus financing arrangement where the bank purchases an item and sells it to the customer at a markup.",
                    metadata={"source": "default_principles.pdf"}
                )
            ]

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(all_docs)
        print(f"📄 Created {len(chunks)} text chunks")

        embedding_model = HuggingFaceEmbeddings()
        # Create a folder for the Chroma database
        persist_directory = os.path.join(self.pdf_folder, "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        # Use Chroma instead of FAISS
        return Chroma.from_documents(
            chunks, 
            embedding_model,
            persist_directory=persist_directory
        )

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        candidates = re.findall(r'```(?:json)?\s*([\s\S]*?)```', text) + re.findall(r'(\{[\s\S]*\})', text)
        for match in candidates:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        try:
            fixed_text = text.replace("'", '"').replace("True", "true").replace("False", "false")
            match = re.search(r'(\{[\s\S]*\})', fixed_text)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass

        print(f"❌ JSON parsing failed for: {text[:300]}...")
        return {}

    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        You are a Shariah compliance assistant. Analyze the following Islamic finance product description and extract structured information. Return only a JSON object with the following fields:

        - "product_type": string
        - "main_parties": list of strings
        - "contract_type": string
        - "key_clauses": list of strings
        - "financial_terms": list of strings
        - "suspicious_terms": list of clauses or phrases that may conflict with Shariah principles

        Text:
        {text}

        Return a valid JSON. Do not include explanations.
        """
        response = self.llm.invoke(prompt)
        print(f"🔍 Raw extraction response:\n{response[:300]}...")
        default = {
            "product_type": None,
            "main_parties": [],
            "contract_type": None,
            "key_clauses": [],
            "financial_terms": [],
            "suspicious_terms": []
        }
        return {**default, **self._safe_parse_json(response)}

    def check_clause_compliance(self, clause: str) -> dict:
        prompt = f"""
        You are a Shariah compliance expert. Assess the following clause from an Islamic finance product and decide whether it may violate Shariah principles. Provide a JSON response with the following structure:

        {{
          "clause": "...",
          "compliant": true/false,
          "reason": "..."
        }}

        Clause: "{clause}"
        Only return valid JSON.
        """
        response = safe_invoke(self.llm, prompt)
        print(f"🧾 Raw compliance check response:\n{response[:300]}...")
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "clause": clause,
                "compliant": False,
                "reason": "Failed to parse compliance data"
            }

    def find_source_for_clause(self, clause: str) -> Optional[Dict[str, Any]]:
        try:
            results = self.vector_db.similarity_search(clause, k=1)
            if results:
                doc = results[0]
                return {
                    "source_doc": doc.metadata.get("source", "unknown"),
                    "source_text": doc.page_content[:300]
                }
        except Exception as e:
            print(f"❌ Failed to find source: {e}")
        return None

    def suggest_improvement(self, clause: str) -> str:
        prompt = f"""
        A clause in an Islamic finance contract has been flagged as non-compliant:

        "{clause}"

        Suggest a Shariah-compliant alternative or modification to make it acceptable.
        """
        return safe_invoke(self.llm, prompt).strip()

    def classify_severity(self, reason_text: str) -> str:
        reason = reason_text.lower()
        if "riba" in reason:
            return "high"
        elif "gharar" in reason or "uncertainty" in reason:
            return "medium"
        elif "minor issue" in reason or "technicality" in reason:
            return "low"
        return "low"

    def classify_violation_category(self, reason_text: str) -> str:
        reason = reason_text.lower()
        if "riba" in reason:
            return "riba"
        elif "gharar" in reason or "uncertainty" in reason:
            return "gharar"
        elif "haram activity" in reason or "prohibited sector" in reason:
            return "haram activities"
        elif "maysir" in reason:
            return "maysir"
        return "other"

    def audit_product_description(self, text: str) -> dict:
        structured_data = self.extract_structured_data(text)
        suspicious_terms = structured_data.get("suspicious_terms", [])

        audit_results = []
        for clause in suspicious_terms:
            result = self.check_clause_compliance(clause)
            source_info = self.find_source_for_clause(clause)
            if source_info:
                result.update(source_info)

            if not result["compliant"]:
                result["severity"] = self.classify_severity(result["reason"])
                result["category"] = self.classify_violation_category(result["reason"])
                result["suggested_fix"] = self.suggest_improvement(clause)

            audit_results.append(result)
            time.sleep(1.1)  # API rate limit

        violations = [r for r in audit_results if not r["compliant"]]
        overall_ok = all(r["compliant"] for r in audit_results)

        return {
            "product_summary": structured_data,
            "suspicious_clauses": audit_results,
            "violations": violations,
            "overall_compliance": overall_ok
        }


# Example usage
if __name__ == "__main__":
    pdf_folder = "./pdfs"
    assistant = ShariahAuditAssistant(pdf_folder)

    product_text = """
    This Murabaha agreement involves deferred payment terms with added profit markup. 
    The seller retains ownership until full payment. An early payment penalty may apply in cases of default. 
    Liquidity is backed by conventional bonds.
    """

    result = assistant.audit_product_description(product_text)

    import pprint
    pprint.pprint(result)