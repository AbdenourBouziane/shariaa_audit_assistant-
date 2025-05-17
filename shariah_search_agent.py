import os
import requests
import json
from typing import List, Dict, Any, Optional
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

class ShariahSearchAgent:
    """
    Agent responsible for searching external sources for Shariah standards and principles
    when local documents don't contain the necessary information.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the search agent with optional API keys for search services.
        
        Args:
            api_key: API key for search service (if None, will try to use environment variable)
        """
        self.search_api_key = api_key or os.getenv("SEARCH_API_KEY")
        # Default search endpoints that don't require API keys
        self.fallback_endpoints = [
            "https://aaoifi.com/?lang=en/search", 
            "https://api.aaoifi.com/standards/search"     # Example endpoint (fictional)
        ]
        
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((requests.RequestException, ConnectionError))
    )
    def search_standards(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search for Shariah standards and principles related to the query.
        
        Args:
            query: The search query related to Shariah finance
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        # If we have a search API key, use the primary search service
        if self.search_api_key:
            try:
                return self._search_primary_service(query, max_results)
            except Exception as e:
                print(f"⚠️ Primary search failed: {e}. Falling back to alternatives.")
        
        # Otherwise, try to use fallback endpoints or simulated search
        return self._search_fallback(query, max_results)
    
    def _search_primary_service(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using the primary search service (requires API key).
        This is a placeholder implementation - replace with actual API integration.
        """
        # Example with SerpAPI (replace with your preferred search API)
        headers = {
            "X-API-Key": self.search_api_key,
            "Content-Type": "application/json"
        }
        
        params = {
            "q": f"islamic finance shariah standards {query}",
            "num": max_results
        }
        
        response = requests.get(
            "https://serpapi.com/search", 
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            # Process and extract relevant information
            results = []
            for item in data.get("organic_results", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("link", ""),
                    "source_type": "search"
                })
            return results
        
        raise Exception(f"Search API error: {response.status_code}")
    
    def _search_fallback(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Use fallback search methods when the primary search is unavailable.
        """
        # Try each fallback endpoint
        for endpoint in self.fallback_endpoints:
            try:
                response = requests.get(
                    endpoint,
                    params={"q": query, "limit": max_results},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Process according to the expected format of each endpoint
                    # This is a placeholder - adjust to actual endpoint responses
                    results = []
                    for item in data.get("results", [])[:max_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "snippet": item.get("content", ""),
                            "source": item.get("url", endpoint),
                            "source_type": "specialized_database"
                        })
                    return results
            except Exception as e:
                print(f"Fallback search to {endpoint} failed: {e}")
                continue
        
        # If all else fails, return simulated results based on common knowledge
        return self._simulate_search_results(query, max_results)
    
    def _simulate_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        When external search fails, provide simulated results based on
        common Shariah finance knowledge.
        """
        # Basic dictionary of common Shariah finance concepts
        shariah_concepts = {
            "riba": [
                {
                    "title": "Prohibition of Riba (Interest)",
                    "snippet": "Riba is strictly prohibited in Islamic finance. It refers to any excess compensation without due consideration. This includes interest on loans and investments.",
                    "source": "AAOIFI Shariah Standard No. 21",
                    "source_type": "simulated"
                },
                {
                    "title": "Types of Riba",
                    "snippet": "Riba al-nasiah (riba of delay) occurs in loans where payment is delayed. Riba al-fadl (riba of excess) occurs in exchanges of similar commodities with unequal amounts.",
                    "source": "Islamic Financial Services Board",
                    "source_type": "simulated"
                }
            ],
            "gharar": [
                {
                    "title": "Prohibition of Gharar (Uncertainty)",
                    "snippet": "Gharar refers to excessive uncertainty or ambiguity in contracts. Islamic finance requires that all terms and conditions be clear, transparent and certain.",
                    "source": "AAOIFI Shariah Standard No. 31",
                    "source_type": "simulated"
                }
            ],
            "maysir": [
                {
                    "title": "Prohibition of Maysir (Gambling)",
                    "snippet": "Maysir refers to any form of gambling or speculation. Islamic finance prohibits transactions that involve gambling or pure speculation without productive economic activity.",
                    "source": "AAOIFI Shariah Standard No. 14",
                    "source_type": "simulated"
                }
            ],
            "mudarabah": [
                {
                    "title": "Mudarabah (Profit-Sharing)",
                    "snippet": "Mudarabah is a partnership where one party provides capital and the other provides expertise. Profits are shared according to an agreed ratio, while losses are borne by the capital provider.",
                    "source": "AAOIFI Shariah Standard No. 13",
                    "source_type": "simulated"
                }
            ],
            "musharakah": [
                {
                    "title": "Musharakah (Joint Venture)",
                    "snippet": "Musharakah is a partnership where all parties contribute capital. Profits are shared according to an agreed ratio, while losses are shared proportionally to capital contributions.",
                    "source": "AAOIFI Shariah Standard No. 12",
                    "source_type": "simulated"
                }
            ],
            "murabaha": [
                {
                    "title": "Murabaha (Cost-Plus Financing)",
                    "snippet": "Murabaha is a sale contract where the seller explicitly declares the cost and profit margin. In Islamic banking, the bank purchases an asset and sells it to the client at a markup.",
                    "source": "AAOIFI Shariah Standard No. 8",
                    "source_type": "simulated"
                }
            ],
            "ijarah": [
                {
                    "title": "Ijarah (Leasing)",
                    "snippet": "Ijarah is a contract where the owner transfers the usufruct of an asset to another person for an agreed period at an agreed consideration. Similar to leasing in conventional finance.",
                    "source": "AAOIFI Shariah Standard No. 9",
                    "source_type": "simulated"
                }
            ],
            "sukuk": [
                {
                    "title": "Sukuk (Islamic Bonds)",
                    "snippet": "Sukuk are certificates representing ownership in an underlying asset, service, project, or investment. Unlike conventional bonds, they don't involve interest payments.",
                    "source": "AAOIFI Shariah Standard No. 17",
                    "source_type": "simulated"
                }
            ],
            "takaful": [
                {
                    "title": "Takaful (Islamic Insurance)",
                    "snippet": "Takaful is based on mutual cooperation where participants contribute to a fund that is used to support members who suffer a defined loss. It avoids the elements of conventional insurance prohibited by Shariah.",
                    "source": "AAOIFI Shariah Standard No. 26",
                    "source_type": "simulated"
                }
            ]
        }
        
        # Search for keywords in the query and return relevant results
        results = []
        query_lower = query.lower()
        
        for keyword, keyword_results in shariah_concepts.items():
            if keyword in query_lower:
                results.extend(keyword_results)
                if len(results) >= max_results:
                    return results[:max_results]
        
        # If no specific matches, return general Islamic finance principles
        if not results:
            results = [
                {
                    "title": "General Shariah Compliance Principles",
                    "snippet": "Islamic finance prohibits interest (riba), excessive uncertainty (gharar), gambling (maysir), and investment in prohibited activities (haram).",
                    "source": "General Shariah Principles",
                    "source_type": "simulated"
                },
                {
                    "title": "Shariah Governance Framework",
                    "snippet": "Islamic financial institutions typically have a Shariah Supervisory Board that ensures all products and operations comply with Islamic principles.",
                    "source": "IFSB Standard No. 10",
                    "source_type": "simulated"
                }
            ]
        
        return results[:max_results]

    def get_detailed_standard(self, standard_reference: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific Shariah standard.
        
        Args:
            standard_reference: Reference identifier for the standard (e.g., "AAOIFI Standard No. 8")
            
        Returns:
            Dictionary containing detailed information about the standard
        """
        # This would normally call an API to get detailed information
        # For now, we'll return simulated data
        
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
            "AAOIFI Shariah Standard No. 9": {
                "title": "Ijarah and Ijarah Muntahia Bittamleek",
                "summary": "This standard covers the rules for leasing (Ijarah) and lease ending with ownership (Ijarah Muntahia Bittamleek).",
                "key_requirements": [
                    "The leased asset must be valuable, identifiable and usable",
                    "Maintenance of the leased asset is the responsibility of the lessor",
                    "The rental amount and period must be clearly specified",
                    "The transfer of ownership in Ijarah Muntahia Bittamleek requires a separate contract"
                ],
                "source": "Accounting and Auditing Organization for Islamic Financial Institutions"
            }
            # Add more standards as needed
        }
        
        # Try to find an exact match
        if standard_reference in standards_details:
            return standards_details[standard_reference]
        
        # Try to find a partial match
        for ref, details in standards_details.items():
            if standard_reference.lower() in ref.lower():
                return details
        
        # Return a generic response if no match is found
        return {
            "title": "Standard Not Found",
            "summary": f"Detailed information for {standard_reference} is not available.",
            "key_requirements": [],
            "source": "N/A"
        }