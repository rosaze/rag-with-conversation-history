# RAG Experiment Platform

A comprehensive research platform for comparing different RAG (Retrieval-Augmented Generation) approaches with conversation history integration. This project evaluates four distinct methodologies across domain-specific scenarios to validate research hypotheses about RAG effectiveness.

## Features

- **Four RAG Approaches**: Compare LLM-only, LLM+history, RAG, and RAG+history methods
- **Real-time Search Integration**: Tavily API for up-to-date information retrieval
- **Quality Evaluation System**: Automated response quality assessment
- **Domain-specific Testing**: Medical, technical, legal, and investment scenarios
- **Interactive Web Interface**: Streamlit-based UI for easy experimentation
- **Comprehensive Logging**: Detailed experiment results and token usage tracking

## Installation

### 1. Clone Repository
```bash
git clone <repository_url>
cd rag-experiment-platform
```

### 2. Python Environment Setup
```bash
# Python 3.11 이상 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install openai pandas streamlit requests
```

### 4. API Configuration
```bash
# 환경변수 설정 (Windows)
set OPENAI_API_KEY=sk-your-openai-key-here
set TAVILY_API_KEY=tvly-dev-your-tavily-key-here

# 환경변수 설정 (Mac/Linux)
export OPENAI_API_KEY=sk-your-openai-key-here
export TAVILY_API_KEY=tvly-dev-your-tavily-key-here
```

또는 `.env` 파일 생성:
```bash
# .env 파일 내용
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-dev-your-tavily-key-here
```

## Usage

### Command Line Experiments

#### Quality-focused Evaluation (Recommended)
```bash
python enhanced_test.py
```

#### Simple Single Scenario Test
```bash
python simple_test.py
```

#### Full Batch Testing (10 scenarios)
```bash
python batch_test.py
```

#### Search API Testing
```bash
python test_with_search.py
```

### Web Interface
```bash
streamlit run app.py
# Access at http://localhost:8501
```

## Project Structure
```
rag-experiment-platform/
├── config/                 # Configuration files
│   ├── settings.py        # API keys and model parameters
│   └── prompts.py         # System prompts for different approaches
├── data/                  # Scenarios and results
│   └── scenarios.json     # Test scenarios with conversation history
├── experiments/           # Experiment execution
│   └── experiment_runner.py  # Main experiment orchestrator
├── src/                   # Core modules
│   ├── llm_handler.py     # OpenAI API interactions
│   ├── search_handler.py  # Tavily search integration
│   ├── query_enhancer.py  # History-based query enhancement
│   └── evaluator.py       # Response quality evaluation
├── utils/                 # Utility functions
│   └── helpers.py         # Common helper functions
├── enhanced_test.py       # Quality-focused experiment (recommended)
├── simple_test.py         # Single scenario test
├── batch_test.py          # Full batch testing
├── test_with_search.py    # Search API validation
└── app.py                 # Streamlit web interface
```

## Research Findings

### Hypothesis Testing Results

**H1: RAG > LLM-only** ❌ **Rejected**
- RAG: 3.27/10 vs LLM-only: 4.55/10
- Simple RAG actually performed worse than LLM-only

**H2: History-enhanced > Simple queries** ✅ **Validated**
- RAG+History: 4.84/10 vs RAG: 3.27/10
- Conversation history significantly improves response quality

### Key Insights

1. **RAG Limitations**: Simple RAG without proper context can degrade response quality
2. **History Importance**: Conversation history is more critical than search augmentation
3. **Domain Variance**: Medical and technical scenarios benefit more from RAG than general topics
4. **Token Efficiency**: RAG increases token usage 5-7x but doesn't guarantee quality improvement

## Results

All experiment results are saved in the `data/` directory as JSON files:
- `enhanced_test_results_*.json` - Quality evaluation results
- `batch_test_results_*.json` - Full scenario testing
- `search_test_results_*.json` - Search API validation

## Contributing

This is a research project. For modifications or extensions:
1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Submit a pull request with detailed research methodology

## License

MIT License - Feel free to use for academic research.