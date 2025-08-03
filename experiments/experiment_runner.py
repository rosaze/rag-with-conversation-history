import json
from datetime import datetime
from src.llm_handler import LLMHandler
from src.search_handler import SearchHandler
from src.query_enhancer import QueryEnhancer
from src.evaluator import ResponseEvaluator

class ExperimentRunner:
    def __init__(self, openai_key, tavily_key=None, search_engine="tavily", 
                 temperature=0.7, max_results=5):
        self.llm_handler = LLMHandler(api_key=openai_key, temperature=temperature)
        
        # Initialize search handler if API key is provided
        self.search_handler = None
        if tavily_key and search_engine:
            try:
                self.search_handler = SearchHandler(engine=search_engine, api_key=tavily_key)
            except Exception as e:
                print(f"Search handler initialization failed: {e}")
        
        self.query_enhancer = QueryEnhancer(self.llm_handler)
        self.evaluator = ResponseEvaluator(self.llm_handler)
        self.max_results = max_results
    
    def run_d1(self, question):
        """D1: LLM-only without conversation history"""
        try:
            result = self.llm_handler.generate_d1_response(question)
            
            return {
                "method": "D1_LLM_ONLY",
                "response": result["response"],
                "usage": result["usage"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "method": "D1_LLM_ONLY",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_d2(self, conversation_history, question):
        """D2: LLM with conversation history"""
        try:
            result = self.llm_handler.generate_d2_response(conversation_history, question)
            
            return {
                "method": "D2_LLM_WITH_HISTORY",
                "response": result["response"],
                "usage": result["usage"],
                "history_length": len(conversation_history),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "method": "D2_LLM_WITH_HISTORY",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_d3(self, question):
        """D3: RAG with current question only"""
        try:
            # Perform search
            search_results = []
            search_data = {}
            
            if self.search_handler:
                search_data = self.search_handler.search(question, self.max_results)
                search_results = search_data.get("results", [])
            
            # Generate response with search results
            result = self.llm_handler.generate_d3_response(question, search_results)
            
            return {
                "method": "D3_RAG_CURRENT_ONLY",
                "response": result["response"],
                "usage": result["usage"],
                "search_results": search_results,
                "search_query": question,
                "search_engine": search_data.get("engine", "none"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "method": "D3_RAG_CURRENT_ONLY",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_d4(self, conversation_history, question):
        """D4: RAG with history-enhanced query"""
        try:
            # Enhance query with conversation history
            query_data = self.query_enhancer.enhance_query(conversation_history, question)
            enhanced_query = query_data["enhanced_query"]
            
            # Perform search with enhanced query
            search_results = []
            search_data = {}
            
            if self.search_handler:
                search_data = self.search_handler.search(enhanced_query, self.max_results)
                search_results = search_data.get("results", [])
            
            # Generate response with search results and history
            result = self.llm_handler.generate_d4_response(conversation_history, question, search_results)
            
            return {
                "method": "D4_RAG_WITH_HISTORY",
                "response": result["response"],
                "usage": result["usage"],
                "search_results": search_results,
                "search_query": enhanced_query,
                "original_question": question,
                "query_enhancement": query_data,
                "history_length": len(conversation_history),
                "search_engine": search_data.get("engine", "none"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "method": "D4_RAG_WITH_HISTORY",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all_methods(self, scenario):
        """Run all 4 methods on a single scenario"""
        results = {}
        
        question = scenario["current_question"]
        history = scenario.get("conversation_history", [])
        
        # Run each method
        results["D1"] = self.run_d1(question)
        results["D2"] = self.run_d2(history, question)
        results["D3"] = self.run_d3(question)
        results["D4"] = self.run_d4(history, question)
        
        return results
    
    def run_experiment_batch(self, scenarios, methods=None):
        """Run experiments on multiple scenarios"""
        if methods is None:
            methods = ["D1", "D2", "D3", "D4"]
        
        all_results = []
        
        for scenario in scenarios:
            scenario_results = {
                "scenario_id": scenario["id"],
                "domain": scenario["domain"],
                "timestamp": datetime.now().isoformat(),
                "results": {}
            }
            
            # Run selected methods
            if "D1" in methods:
                scenario_results["results"]["D1"] = self.run_d1(scenario["current_question"])
            
            if "D2" in methods:
                scenario_results["results"]["D2"] = self.run_d2(
                    scenario.get("conversation_history", []), 
                    scenario["current_question"]
                )
            
            if "D3" in methods:
                scenario_results["results"]["D3"] = self.run_d3(scenario["current_question"])
            
            if "D4" in methods:
                scenario_results["results"]["D4"] = self.run_d4(
                    scenario.get("conversation_history", []), 
                    scenario["current_question"]
                )
            
            # Evaluate results
            if hasattr(self, 'evaluator') and self.evaluator:
                evaluation = self.evaluator.compare_responses(scenario, scenario_results["results"])
                scenario_results["evaluation"] = evaluation
            
            all_results.append(scenario_results)
        
        return all_results
    
    def get_experiment_summary(self, results):
        """Generate summary statistics for experiment results"""
        summary = {
            "total_scenarios": len(results),
            "methods_tested": set(),
            "success_rates": {},
            "average_response_lengths": {},
            "search_statistics": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Collect method statistics
        for result in results:
            for method, method_result in result.get("results", {}).items():
                summary["methods_tested"].add(method)
                
                # Track success/failure
                if method not in summary["success_rates"]:
                    summary["success_rates"][method] = {"success": 0, "total": 0}
                
                summary["success_rates"][method]["total"] += 1
                if "error" not in method_result:
                    summary["success_rates"][method]["success"] += 1
                
                # Track response lengths
                if "response" in method_result:
                    if method not in summary["average_response_lengths"]:
                        summary["average_response_lengths"][method] = []
                    summary["average_response_lengths"][method].append(len(method_result["response"]))
                
                # Track search statistics
                if "search_results" in method_result:
                    if method not in summary["search_statistics"]:
                        summary["search_statistics"][method] = {
                            "total_searches": 0,
                            "total_results": 0,
                            "average_results": 0
                        }
                    summary["search_statistics"][method]["total_searches"] += 1
                    summary["search_statistics"][method]["total_results"] += len(method_result["search_results"])
        
        # Calculate averages
        for method in summary["average_response_lengths"]:
            lengths = summary["average_response_lengths"][method]
            summary["average_response_lengths"][method] = sum(lengths) / len(lengths) if lengths else 0
        
        for method in summary["search_statistics"]:
            stats = summary["search_statistics"][method]
            if stats["total_searches"] > 0:
                stats["average_results"] = stats["total_results"] / stats["total_searches"]
        
        # Calculate success rates as percentages
        for method in summary["success_rates"]:
            rate_data = summary["success_rates"][method]
            rate_data["percentage"] = (rate_data["success"] / rate_data["total"]) * 100 if rate_data["total"] > 0 else 0
        
        return summary
