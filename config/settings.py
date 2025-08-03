import os

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")

# Model Configuration
DEFAULT_MODEL = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 1500

# Search Configuration
MAX_SEARCH_RESULTS = 5
SEARCH_TIMEOUT = 10

# Experiment Configuration
RESULTS_FILE = "data/results.json"
SCENARIOS_FILE = "data/scenarios.json"

# Evaluation Criteria
EVALUATION_CRITERIA = {
    "relevance": {"weight": 0.3, "description": "How relevant is the response to the question"},
    "accuracy": {"weight": 0.3, "description": "Factual correctness of the information"},
    "completeness": {"weight": 0.2, "description": "How complete and comprehensive is the answer"},
    "history_integration": {"weight": 0.2, "description": "How well conversation history is integrated"}
}
