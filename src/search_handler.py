import requests
import json
from config.settings import MAX_SEARCH_RESULTS, SEARCH_TIMEOUT

class SearchHandler:
    def __init__(self, engine="tavily", api_key=None):
        self.engine = engine.lower()
        self.api_key = api_key
        
        if not api_key and engine in ["tavily", "brave"]:
            raise ValueError(f"API key required for {engine} search engine")
    
    def search(self, query, max_results=MAX_SEARCH_RESULTS):
        """Perform web search using the configured engine"""
        if self.engine == "tavily":
            return self._search_tavily(query, max_results)
        elif self.engine == "brave":
            return self._search_brave(query, max_results)
        else:
            raise ValueError(f"Unsupported search engine: {self.engine}")
    
    def _search_tavily(self, query, max_results):
        """Search using Tavily API"""
        try:
            url = "https://api.tavily.com/search"
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_images": False,
                "include_raw_content": False,
                "max_results": max_results
            }
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=SEARCH_TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format Tavily results
            results = []
            for result in data.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", 0)
                })
            
            return {
                "results": results,
                "query": query,
                "engine": "tavily",
                "answer": data.get("answer", "")
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Tavily search failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Tavily search error: {str(e)}")
    
    def _search_brave(self, query, max_results):
        """Search using Brave Search API"""
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": max_results,
                "search_lang": "en",
                "country": "US",
                "safesearch": "moderate"
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=SEARCH_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format Brave results
            results = []
            for result in data.get("web", {}).get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("description", ""),
                    "url": result.get("url", ""),
                    "score": 1.0  # Brave doesn't provide relevance scores
                })
            
            return {
                "results": results,
                "query": query,
                "engine": "brave"
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Brave search failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Brave search error: {str(e)}")
    
    def search_with_fallback(self, query, max_results=MAX_SEARCH_RESULTS):
        """Search with fallback to alternative engine if primary fails"""
        try:
            return self.search(query, max_results)
        except Exception as primary_error:
            # If no API key provided, return empty results instead of failing
            if not self.api_key:
                return {
                    "results": [],
                    "query": query,
                    "engine": "none",
                    "error": "No search API key provided"
                }
            
            # Otherwise, re-raise the error
            raise primary_error
