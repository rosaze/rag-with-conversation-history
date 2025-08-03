import json
import os
from datetime import datetime
from config.settings import SCENARIOS_FILE, RESULTS_FILE

def load_scenarios():
    """Load experiment scenarios from JSON file"""
    try:
        if os.path.exists(SCENARIOS_FILE):
            with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("scenarios", [])
        else:
            print(f"Scenarios file not found: {SCENARIOS_FILE}")
            return []
    except Exception as e:
        print(f"Error loading scenarios: {e}")
        return []

def save_results(results):
    """Save experiment results to JSON file"""
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Load existing results if file exists
        existing_results = []
        if os.path.exists(RESULTS_FILE):
            try:
                with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
            except json.JSONDecodeError:
                print("Existing results file is corrupted, starting fresh")
                existing_results = []
        
        # Append new results
        if isinstance(results, list):
            existing_results.extend(results)
        else:
            existing_results.append(results)
        
        # Save back to file
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_results, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to {RESULTS_FILE}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def load_results():
    """Load experiment results from JSON file"""
    try:
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        print(f"Error loading results: {e}")
        return []

def format_conversation_history(history):
    """Format conversation history for display"""
    if not history:
        return "No conversation history"
    
    formatted = []
    for i, message in enumerate(history, 1):
        formatted.append(f"Turn {i}: {message}")
    
    return "\n".join(formatted)

def calculate_response_metrics(response):
    """Calculate basic metrics for a response"""
    if not response:
        return {
            "word_count": 0,
            "character_count": 0,
            "sentence_count": 0
        }
    
    words = response.split()
    sentences = [s.strip() for s in response.split('.') if s.strip()]
    
    return {
        "word_count": len(words),
        "character_count": len(response),
        "sentence_count": len(sentences)
    }

def export_results_to_csv(results):
    """Export results to CSV format"""
    import pandas as pd
    
    # Flatten results for CSV export
    flattened_data = []
    
    for result in results:
        base_info = {
            "timestamp": result.get("timestamp", ""),
            "scenario_id": result.get("scenario_id", ""),
            "domain": result.get("domain", "")
        }
        
        for method, method_result in result.get("results", {}).items():
            row = base_info.copy()
            row["method"] = method
            row["has_error"] = "error" in method_result
            row["response"] = method_result.get("response", "")
            row["response_length"] = len(row["response"])
            
            # Add method-specific fields
            if "search_results" in method_result:
                row["search_results_count"] = len(method_result["search_results"])
                row["search_query"] = method_result.get("search_query", "")
            
            if "history_length" in method_result:
                row["history_length"] = method_result["history_length"]
            
            flattened_data.append(row)
    
    return pd.DataFrame(flattened_data)

def validate_api_keys(openai_key, search_key=None):
    """Validate API keys format"""
    errors = []
    
    if not openai_key:
        errors.append("OpenAI API key is required")
    elif not openai_key.startswith("sk-"):
        errors.append("OpenAI API key should start with 'sk-'")
    
    if search_key and not search_key.strip():
        errors.append("Search API key cannot be empty if provided")
    
    return errors

def get_scenario_by_id(scenarios, scenario_id):
    """Get a specific scenario by ID"""
    for scenario in scenarios:
        if scenario.get("id") == scenario_id:
            return scenario
    return None

def filter_scenarios_by_domain(scenarios, domain):
    """Filter scenarios by domain"""
    return [s for s in scenarios if s.get("domain", "").lower() == domain.lower()]

def get_domains_from_scenarios(scenarios):
    """Get unique domains from scenarios"""
    domains = set()
    for scenario in scenarios:
        if "domain" in scenario:
            domains.add(scenario["domain"])
    return sorted(list(domains))

def create_experiment_metadata(scenarios, methods, config):
    """Create metadata for an experiment run"""
    return {
        "experiment_id": f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "scenario_count": len(scenarios),
        "methods": methods,
        "config": config,
        "scenarios_tested": [s.get("id") for s in scenarios]
    }

def clean_response_text(text):
    """Clean response text for analysis"""
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = " ".join(text.split())
    
    # Remove common artifacts
    cleaned = cleaned.replace("**", "")  # Remove markdown bold
    cleaned = cleaned.replace("*", "")   # Remove markdown italics
    
    return cleaned.strip()

def calculate_similarity_score(text1, text2):
    """Calculate simple similarity between two texts"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0
