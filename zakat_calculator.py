import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from fpdf import FPDF
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import warnings
warnings.filterwarnings('ignore')

# Define AAOIFI standards for Zakat calculation
AAOIFI_STANDARDS = {
    "FAS_9": {
        "name": "Zakat",
        "nisab_gold": 85,  # grams of gold
        "nisab_silver": 595,  # grams of silver
        "rate": 0.025,  # 2.5%
        "zakatable_assets": [
            "Cash and cash equivalents",
            "Trade receivables",
            "Inventory",
            "Investments (short-term)",
            "Gold and silver",
            "Agricultural produce"
        ],
        "non_zakatable_assets": [
            "Fixed assets",
            "Intangible assets",
            "Long-term investments for operations",
            "Properties for personal use"
        ],
        "deductible_liabilities": [
            "Short-term liabilities",
            "Operational expenses due",
            "Taxes payable"
        ],
        "non_deductible_liabilities": [
            "Long-term debts",
            "Capital investments"
        ]
    }
}

# Current gold and silver prices (these would normally be fetched via API)
METAL_PRICES = {
    "gold_per_gram": 70,  # USD
    "silver_per_gram": 0.85  # USD
}

class ZakatCalculator:
    """
    Core class for calculating Zakat based on AAOIFI standards
    """
    def __init__(self, standard="FAS_9"):
        self.standard = AAOIFI_STANDARDS[standard]
        self.nisab_value = max(
            self.standard["nisab_gold"] * METAL_PRICES["gold_per_gram"],
            self.standard["nisab_silver"] * METAL_PRICES["silver_per_gram"]
        )
        self.rate = self.standard["rate"]
        
    def classify_accounts(self, financial_data):
        """
        Classifies accounts as zakatable, non-zakatable, or deductible
        """
        classified = {
            "zakatable_assets": {},
            "non_zakatable_assets": {},
            "deductible_liabilities": {},
            "non_deductible_liabilities": {}
        }
        
        # For each account in balance sheet
        for account, value in financial_data["balance_sheet"].items():
            account_lower = account.lower()
            
            # Classify using simple keyword matching (would be more sophisticated in production)
            if any(keyword in account_lower for keyword in ["cash", "bank", "receivable", "inventory", "investment", "gold", "silver"]):
                classified["zakatable_assets"][account] = value
            elif any(keyword in account_lower for keyword in ["property", "equipment", "building", "intangible", "goodwill"]):
                classified["non_zakatable_assets"][account] = value
            elif any(keyword in account_lower for keyword in ["payable", "accrued", "tax", "short term"]):
                classified["deductible_liabilities"][account] = value
            elif any(keyword in account_lower for keyword in ["loan", "long term", "capital"]):
                classified["non_deductible_liabilities"][account] = value
        
        return classified
    
    def calculate_zakat_base(self, financial_data):
        """
        Calculate Zakat base according to AAOIFI FAS 9
        """
        classified = self.classify_accounts(financial_data)
        
        # Net Asset Method (most common in AAOIFI)
        total_zakatable_assets = sum(classified["zakatable_assets"].values())
        total_deductible_liabilities = sum(classified["deductible_liabilities"].values())
        
        zakat_base = total_zakatable_assets - total_deductible_liabilities
        
        return {
            "classified_accounts": classified,
            "total_zakatable_assets": total_zakatable_assets,
            "total_deductible_liabilities": total_deductible_liabilities,
            "zakat_base": zakat_base
        }
    
    def calculate_zakat_amount(self, financial_data):
        """
        Calculate final Zakat amount
        """
        calculation = self.calculate_zakat_base(financial_data)
        zakat_base = calculation["zakat_base"]
        
        # Check if wealth meets Nisab threshold
        if zakat_base < self.nisab_value:
            calculation["zakat_due"] = 0
            calculation["exceeds_nisab"] = False
            calculation["zakat_amount"] = 0
        else:
            calculation["zakat_due"] = True
            calculation["exceeds_nisab"] = True
            calculation["zakat_amount"] = zakat_base * self.rate
        
        # Add additional information
        calculation["nisab_value"] = self.nisab_value
        calculation["zakat_rate"] = self.rate
        calculation["calculation_date"] = datetime.now().strftime("%Y-%m-%d")
        
        return calculation


class ZakatComplianceAdvisor:
    """
    Uses AI to provide compliance advice and optimization suggestions
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy_key")
        self.llm = ChatOpenAI(temperature=0, openai_api_key=self.api_key)
        
    def get_compliance_advice(self, financial_data, calculation_results):
        """
        Generate compliance advice based on financial data and calculation results
        """
        prompt = f"""
        As an Islamic Finance expert, analyze the following Zakat calculation results and provide
        compliance advice according to AAOIFI FAS 9 standards:
        
        Financial Summary:
        - Total zakatable assets: ${calculation_results['total_zakatable_assets']:,.2f}
        - Total deductible liabilities: ${calculation_results['total_deductible_liabilities']:,.2f}
        - Zakat base: ${calculation_results['zakat_base']:,.2f}
        - Nisab threshold: ${calculation_results['nisab_value']:,.2f}
        - Zakat amount due: ${calculation_results['zakat_amount']:,.2f}
        
        Please provide:
        1. An assessment of compliance with AAOIFI standards
        2. Any potential issues or concerns with the classification of assets/liabilities
        3. Recommendations for improving Zakat compliance
        4. Any relevant Shariah considerations
        
        Keep your response concise and focused on practical advice.
        """
        
        messages = [
            SystemMessage(content="You are an Islamic Finance expert specializing in Zakat compliance according to AAOIFI standards."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm(messages)
            return response.content
        except Exception as e:
            return f"Error generating compliance advice: {str(e)}"
    
    def get_optimization_suggestions(self, financial_data, calculation_results):
        """
        Generate Zakat optimization suggestions within Shariah boundaries
        """
        prompt = f"""
        As an Islamic Finance expert, provide legitimate Zakat optimization strategies for the following financial situation:
        
        Financial Summary:
        - Total zakatable assets: ${calculation_results['total_zakatable_assets']:,.2f}
        - Total deductible liabilities: ${calculation_results['total_deductible_liabilities']:,.2f}
        - Zakat base: ${calculation_results['zakat_base']:,.2f}
        - Zakat amount due: ${calculation_results['zakat_amount']:,.2f}
        
        Provide 3-5 specific, actionable suggestions for Zakat optimization that:
        1. Comply fully with Shariah principles
        2. Follow AAOIFI FAS 9 standards
        3. Are practical for implementation
        
        For each suggestion, briefly explain how it works and why it's Shariah-compliant.
        """
        
        messages = [
            SystemMessage(content="You are an Islamic Finance expert specializing in Shariah-compliant Zakat optimization."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm(messages)
            return response.content
        except Exception as e:
            return f"Error generating optimization suggestions: {str(e)}"


class ZakatDocumentGenerator:
    """
    Generates Zakat compliance documentation
    """
    def generate_zakat_certificate(self, entity_info, calculation_results):
        """
        Generate a Zakat payment certificate
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "ZAKAT COMPLIANCE CERTIFICATE", ln=True, align="C")
        pdf.ln(10)
        
        # Entity Information
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Entity Information", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(60, 8, "Entity Name:", 0)
        pdf.cell(0, 8, entity_info.get("name", ""), ln=True)
        pdf.cell(60, 8, "Registration Number:", 0)
        pdf.cell(0, 8, entity_info.get("registration", ""), ln=True)
        pdf.cell(60, 8, "Zakat Year:", 0)
        pdf.cell(0, 8, entity_info.get("zakat_year", ""), ln=True)
        pdf.ln(10)
        
        # Calculation Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Zakat Calculation Summary", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(60, 8, "Total Zakatable Assets:", 0)
        pdf.cell(0, 8, f"${calculation_results['total_zakatable_assets']:,.2f}", ln=True)
        pdf.cell(60, 8, "Total Deductible Liabilities:", 0)
        pdf.cell(0, 8, f"${calculation_results['total_deductible_liabilities']:,.2f}", ln=True)
        pdf.cell(60, 8, "Zakat Base:", 0)
        pdf.cell(0, 8, f"${calculation_results['zakat_base']:,.2f}", ln=True)
        pdf.cell(60, 8, "Nisab Threshold:", 0)
        pdf.cell(0, 8, f"${calculation_results['nisab_value']:,.2f}", ln=True)
        pdf.cell(60, 8, "Zakat Rate:", 0)
        pdf.cell(0, 8, f"{calculation_results['zakat_rate'] * 100}%", ln=True)
        pdf.cell(60, 8, "Zakat Amount Due:", 0)
        pdf.cell(0, 8, f"${calculation_results['zakat_amount']:,.2f}", ln=True)
        pdf.ln(10)
        
        # Compliance Statement
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Compliance Statement", ln=True)
        pdf.set_font("Arial", "", 12)
        compliance_text = "This is to certify that the above Zakat calculation has been performed in accordance with AAOIFI FAS 9 standards."
        pdf.multi_cell(0, 8, compliance_text)
        pdf.ln(10)
        
        # Signature
        pdf.cell(60, 8, "Date of Calculation:", 0)
        pdf.cell(0, 8, calculation_results["calculation_date"], ln=True)
        pdf.ln(20)
        pdf.cell(80, 8, "Authorized Signature:", 0)
        pdf.cell(0, 8, "_________________________", ln=True)
        
        # Save the PDF to a temporary file
        filename = f"zakat_certificate_{entity_info.get('name', 'entity').replace(' ', '_')}.pdf"
        pdf.output(filename)
        return filename
    
    def generate_detailed_report(self, entity_info, financial_data, calculation_results, compliance_advice):
        """
        Generate a detailed Zakat compliance report
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "DETAILED ZAKAT COMPLIANCE REPORT", ln=True, align="C")
        pdf.ln(10)
        
        # Entity Information
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Entity Information", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(60, 8, "Entity Name:", 0)
        pdf.cell(0, 8, entity_info.get("name", ""), ln=True)
        pdf.cell(60, 8, "Registration Number:", 0)
        pdf.cell(0, 8, entity_info.get("registration", ""), ln=True)
        pdf.cell(60, 8, "Zakat Year:", 0)
        pdf.cell(0, 8, entity_info.get("zakat_year", ""), ln=True)
        pdf.ln(10)
        
        # Asset Classification
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Asset Classification", ln=True)
        pdf.set_font("Arial", "", 12)
        
        # Zakatable Assets
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Zakatable Assets:", ln=True)
        pdf.set_font("Arial", "", 11)
        for asset, value in calculation_results["classified_accounts"]["zakatable_assets"].items():
            pdf.cell(100, 6, asset, 0)
            pdf.cell(0, 6, f"${value:,.2f}", ln=True)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(100, 8, "Total Zakatable Assets:", 0)
        pdf.cell(0, 8, f"${calculation_results['total_zakatable_assets']:,.2f}", ln=True)
        pdf.ln(5)
        
        # Non-Zakatable Assets
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Non-Zakatable Assets:", ln=True)
        pdf.set_font("Arial", "", 11)
        for asset, value in calculation_results["classified_accounts"]["non_zakatable_assets"].items():
            pdf.cell(100, 6, asset, 0)
            pdf.cell(0, 6, f"${value:,.2f}", ln=True)
        pdf.ln(5)
        
        # Deductible Liabilities
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Deductible Liabilities:", ln=True)
        pdf.set_font("Arial", "", 11)
        for liability, value in calculation_results["classified_accounts"]["deductible_liabilities"].items():
            pdf.cell(100, 6, liability, 0)
            pdf.cell(0, 6, f"${value:,.2f}", ln=True)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(100, 8, "Total Deductible Liabilities:", 0)
        pdf.cell(0, 8, f"${calculation_results['total_deductible_liabilities']:,.2f}", ln=True)
        pdf.ln(10)
        
        # Calculation Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Zakat Calculation Summary", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(100, 8, "Zakat Base:", 0)
        pdf.cell(0, 8, f"${calculation_results['zakat_base']:,.2f}", ln=True)
        pdf.cell(100, 8, "Nisab Threshold:", 0)
        pdf.cell(0, 8, f"${calculation_results['nisab_value']:,.2f}", ln=True)
        pdf.cell(100, 8, "Exceeds Nisab:", 0)
        pdf.cell(0, 8, "Yes" if calculation_results['exceeds_nisab'] else "No", ln=True)
        pdf.cell(100, 8, "Zakat Rate:", 0)
        pdf.cell(0, 8, f"{calculation_results['zakat_rate'] * 100}%", ln=True)
        pdf.cell(100, 8, "Zakat Amount Due:", 0)
        pdf.cell(0, 8, f"${calculation_results['zakat_amount']:,.2f}", ln=True)
        pdf.ln(10)
        
        # Add a new page for compliance advice
        pdf.add_page()
        
        # Compliance Advice
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Compliance Assessment & Recommendations", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, compliance_advice)
        
        # Save the PDF to a temporary file
        filename = f"zakat_detailed_report_{entity_info.get('name', 'entity').replace(' ', '_')}.pdf"
        pdf.output(filename)
        return filename


def create_sample_financial_data():
    """
    Create sample financial data for demonstration
    """
    return {
        "balance_sheet": {
            "Cash and bank balances": 120000,
            "Trade receivables": 350000,
            "Inventory": 485000,
            "Short-term investments": 275000,
            "Prepaid expenses": 45000,
            "Property and equipment": 1250000,
            "Intangible assets": 350000,
            "Long-term investments": 500000,
            "Trade payables": 280000,
            "Accrued expenses": 95000,
            "Short-term borrowings": 150000,
            "Tax payable": 75000,
            "Long-term loans": 650000,
            "Share capital": 1000000,
            "Retained earnings": 725000
        }
    }


def main():
    st.set_page_config(page_title="Islamic Finance Zakat Calculator", layout="wide")
    
    st.title("Islamic Finance Zakat Calculator")
    st.write("Based on AAOIFI FAS 9 Standards")
    
    # Input section
    st.header("Entity Information")
    col1, col2 = st.columns(2)
    with col1:
        entity_name = st.text_input("Entity Name", "Sample Business LLC")
        registration_number = st.text_input("Registration Number", "REG12345")
    with col2:
        zakat_year = st.text_input("Zakat Year", "2025")
        calculation_date = st.date_input("Calculation Date", datetime.now())
    
    # Financial data input
    st.header("Financial Data")
    st.write("Enter your balance sheet information:")
    
    # Load sample data
    sample_data = create_sample_financial_data()
    use_sample = st.checkbox("Use sample data for demonstration", True)
    
    if use_sample:
        financial_data = sample_data
    else:
        financial_data = {"balance_sheet": {}}
        
        # Dynamic form for balance sheet entries
        st.subheader("Assets")
        col1, col2 = st.columns(2)
        with col1:
            cash = st.number_input("Cash and bank balances", value=0.0, format="%.2f")
            receivables = st.number_input("Trade receivables", value=0.0, format="%.2f")
            inventory = st.number_input("Inventory", value=0.0, format="%.2f")
            short_investments = st.number_input("Short-term investments", value=0.0, format="%.2f")
            prepaid = st.number_input("Prepaid expenses", value=0.0, format="%.2f")
        with col2:
            property_equipment = st.number_input("Property and equipment", value=0.0, format="%.2f")
            intangible = st.number_input("Intangible assets", value=0.0, format="%.2f")
            long_investments = st.number_input("Long-term investments", value=0.0, format="%.2f")
        
        st.subheader("Liabilities and Equity")
        col1, col2 = st.columns(2)
        with col1:
            payables = st.number_input("Trade payables", value=0.0, format="%.2f")
            accrued = st.number_input("Accrued expenses", value=0.0, format="%.2f")
            short_borrowings = st.number_input("Short-term borrowings", value=0.0, format="%.2f")
            tax_payable = st.number_input("Tax payable", value=0.0, format="%.2f")
        with col2:
            long_loans = st.number_input("Long-term loans", value=0.0, format="%.2f")
            share_capital = st.number_input("Share capital", value=0.0, format="%.2f")
            retained = st.number_input("Retained earnings", value=0.0, format="%.2f")
            
        # Update financial data
        financial_data["balance_sheet"] = {
            "Cash and bank balances": cash,
            "Trade receivables": receivables,
            "Inventory": inventory,
            "Short-term investments": short_investments,
            "Prepaid expenses": prepaid,
            "Property and equipment": property_equipment,
            "Intangible assets": intangible,
            "Long-term investments": long_investments,
            "Trade payables": payables,
            "Accrued expenses": accrued,
            "Short-term borrowings": short_borrowings,
            "Tax payable": tax_payable,
            "Long-term loans": long_loans,
            "Share capital": share_capital,
            "Retained earnings": retained
        }
    
    # Process button
    if st.button("Calculate Zakat"):
        # Calculate Zakat
        calculator = ZakatCalculator()
        calculation_results = calculator.calculate_zakat_amount(financial_data)
        
        # Display results
        st.header("Zakat Calculation Results")
        
        # Summary
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Zakatable Assets", f"${calculation_results['total_zakatable_assets']:,.2f}")
        with col2:
            st.metric("Total Deductible Liabilities", f"${calculation_results['total_deductible_liabilities']:,.2f}")
        with col3:
            st.metric("Zakat Base", f"${calculation_results['zakat_base']:,.2f}")
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nisab Threshold", f"${calculation_results['nisab_value']:,.2f}")
        with col2:
            st.metric("Exceeds Nisab", "Yes" if calculation_results['exceeds_nisab'] else "No")
        with col3:
            st.metric("Zakat Amount Due", f"${calculation_results['zakat_amount']:,.2f}")
        
        # Detailed breakdown
        st.subheader("Detailed Breakdown")
        
        # Zakatable Assets
        st.write("**Zakatable Assets**")
        asset_df = pd.DataFrame(list(calculation_results["classified_accounts"]["zakatable_assets"].items()), 
                               columns=["Account", "Amount"])
        st.dataframe(asset_df)
        
        # Deductible Liabilities
        st.write("**Deductible Liabilities**")
        liability_df = pd.DataFrame(list(calculation_results["classified_accounts"]["deductible_liabilities"].items()), 
                                  columns=["Account", "Amount"])
        st.dataframe(liability_df)
        
        # Generate compliance advice (mock for demo purposes)
        st.header("Compliance Analysis")
        
        # Create advisor object
        advisor = ZakatComplianceAdvisor()
        
        # This section would use the LLM in a real implementation
        # For demo, we'll use sample responses
        if not os.getenv("OPENAI_API_KEY"):
            compliance_advice = """
            Based on the financial data provided and Zakat calculation results:
            
            1. **Compliance Assessment:**
               - The calculation follows AAOIFI FAS 9 requirements for classifying zakatable assets and deductible liabilities
               - The net asset method has been correctly applied
               - The Nisab threshold comparison is appropriate
            
            2. **Potential Issues:**
               - Short-term investments should be further classified to ensure they don't include non-zakatable securities
               - Verify that trade receivables are expected to be collected (doubtful debts may be excluded)
            
            3. **Recommendations:**
               - Maintain separate accounting records for Zakat throughout the year
               - Consider distributing Zakat on a quarterly basis for more consistent cash flow management
               - Document detailed asset classifications for audit purposes
            
            4. **Shariah Considerations:**
               - Ensure Zakat is distributed to eligible recipients as specified in Shariah
               - Verify timing of calculation aligns with Islamic calendar
            """
            
            optimization_suggestions = """
            Here are Shariah-compliant Zakat optimization strategies:
            
            1. **Accelerate Receivable Collection:**
               - Collect trade receivables before the Zakat calculation date
               - This converts potentially uncollectible amounts (which might be excluded) into definite zakatable cash
               - Shariah-compliant because it represents actual business improvement, not artificial manipulation
            
            2. **Advance Payment of Short-term Liabilities:**
               - Pay outstanding short-term liabilities before calculation date
               - This is legitimate as these are actual business expenses that reduce zakatable wealth
               - Compliant because it represents actual settlement of obligations
            
            3. **Inventory Management:**
               - Complete sales of inventory nearing calculation date
               - Time major inventory purchases after calculation date
               - Permitted as it represents normal business operations
            
            4. **Invest in Productive Business Assets:**
               - Convert zakatable assets into non-zakatable productive business assets
               - AAOIFI standards exempt assets used in production/operations
               - Shariah-compliant as it promotes economic development
            
            5. **Timing of Zakat Year:**
               - Choose a fiscal Zakat year when business typically has lower liquid assets
               - Permissible as long as a full lunar year (Hawl) passes between calculations
            """
        else:
            compliance_advice = advisor.get_compliance_advice(financial_data, calculation_results)
            optimization_suggestions = advisor.get_optimization_suggestions(financial_data, calculation_results)
        
        st.subheader("Compliance Assessment")
        st.write(compliance_advice)
        
        st.subheader("Optimization Suggestions")
        st.write(optimization_suggestions)
        
        # Document Generation
        st.header("Documentation")
        
        entity_info = {
            "name": entity_name,
            "registration": registration_number,
            "zakat_year": zakat_year
        }
        
        doc_generator = ZakatDocumentGenerator()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Zakat Certificate"):
                cert_file = doc_generator.generate_zakat_certificate(entity_info, calculation_results)
                st.success(f"Zakat Certificate generated: {cert_file}")
                
        with col2:
            if st.button("Generate Detailed Report"):
                report_file = doc_generator.generate_detailed_report(entity_info, financial_data, 
                                                                    calculation_results, compliance_advice)
                st.success(f"Detailed Report generated: {report_file}")


if __name__ == "__main__":
    main()