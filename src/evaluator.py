import json
from datetime import datetime
from config.settings import EVALUATION_CRITERIA

class ResponseEvaluator:
    def __init__(self, llm_handler=None):
        self.llm_handler = llm_handler
        self.criteria = EVALUATION_CRITERIA
    
    def evaluate_response(self, scenario, response_data, method):
        """Evaluate a single response against the scenario"""
        try:
            evaluation = {
                "scenario_id": scenario["id"],
                "domain": scenario["domain"],
                "method": method,
                "timestamp": datetime.now().isoformat(),
                "response_length": len(response_data.get("response", "")),
                "has_error": "error" in response_data
            }
            
            if not evaluation["has_error"]:
                # Add automated metrics
                evaluation.update(self._calculate_automated_metrics(scenario, response_data))
                
                # Add LLM-based evaluation if available
                if self.llm_handler:
                    llm_eval = self._llm_evaluation(scenario, response_data)
                    evaluation["llm_evaluation"] = llm_eval
            
            return evaluation
            
        except Exception as e:
            return {
                "scenario_id": scenario["id"],
                "method": method,
                "error": f"Evaluation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_automated_metrics(self, scenario, response_data):
        """Calculate automated metrics without LLM"""
        response = response_data.get("response", "")
        expected_focus = scenario.get("expected_focus", [])
        
        # Focus area coverage (simple keyword matching)
        focus_coverage = self._calculate_focus_coverage(response, expected_focus)
        
        # Response characteristics
        metrics = {
            "focus_coverage": focus_coverage,
            "response_characteristics": {
                "word_count": len(response.split()),
                "sentence_count": len([s for s in response.split('.') if s.strip()]),
                "has_numbers": any(char.isdigit() for char in response),
                "has_technical_terms": self._has_technical_terms(response, scenario["domain"])
            }
        }
        
        # Search-specific metrics
        if "search_results" in response_data:
            metrics["search_metrics"] = {
                "results_used": len(response_data["search_results"]),
                "search_query": response_data.get("search_query", ""),
                "search_engine": response_data.get("search_engine", "")
            }
        
        return metrics
    
    def _calculate_focus_coverage(self, response, expected_focus):
        """Calculate how well the response covers expected focus areas"""
        if not expected_focus:
            return 0.0
        
        response_lower = response.lower()
        covered_areas = 0
        
        for focus_area in expected_focus:
            # Simple keyword matching
            if focus_area.lower() in response_lower:
                covered_areas += 1
            else:
                # Check for partial matches or related terms
                focus_words = focus_area.lower().split()
                if any(word in response_lower for word in focus_words if len(word) > 3):
                    covered_areas += 0.5
        
        return covered_areas / len(expected_focus)
    
    def _has_technical_terms(self, response, domain):
        """Check if response contains domain-appropriate technical terms"""
        technical_indicators = {
            "의료상담": ["증상", "진단", "치료", "병원", "의사", "약물", "검사"],
            "기술지원": ["설정", "코드", "오류", "시스템", "설치", "버전", "API"],
            "법률자문": ["법률", "계약", "권리", "의무", "법원", "판례", "조항"],
            "투자상담": ["투자", "수익", "위험", "포트폴리오", "자산", "금리", "시장"],
            "IT보안": ["보안", "암호화", "접근", "권한", "인증", "방화벽", "취약점"]
        }
        
        indicators = technical_indicators.get(domain, [])
        response_lower = response.lower()
        
        return any(term in response_lower for term in indicators)
    
    def _llm_evaluation(self, scenario, response_data):
        """Use LLM to evaluate response quality"""
        if not self.llm_handler:
            return None
        
        try:
            evaluation = self.llm_handler.evaluate_response(
                question=scenario["current_question"],
                history=scenario.get("conversation_history", []),
                response=response_data["response"]
            )
            return evaluation
        except Exception as e:
            return {"error": f"LLM evaluation failed: {str(e)}"}
    
    def compare_responses(self, scenario, all_responses):
        """Compare multiple responses for the same scenario"""
        evaluations = {}
        
        for method, response_data in all_responses.items():
            evaluations[method] = self.evaluate_response(scenario, response_data, method)
        
        # Add comparative metrics
        comparison = {
            "scenario_id": scenario["id"],
            "domain": scenario["domain"],
            "evaluations": evaluations,
            "comparison_metrics": self._calculate_comparison_metrics(evaluations)
        }
        
        return comparison
    
    def _calculate_comparison_metrics(self, evaluations):
        """Calculate metrics that compare different methods"""
        metrics = {}
        
        # Response length comparison
        lengths = {method: eval_data.get("response_length", 0) 
                  for method, eval_data in evaluations.items() 
                  if not eval_data.get("has_error", False)}
        
        if lengths:
            metrics["length_comparison"] = {
                "longest": max(lengths, key=lengths.get),
                "shortest": min(lengths, key=lengths.get),
                "length_variance": max(lengths.values()) - min(lengths.values())
            }
        
        # Focus coverage comparison
        coverages = {method: eval_data.get("focus_coverage", 0) 
                    for method, eval_data in evaluations.items() 
                    if not eval_data.get("has_error", False)}
        
        if coverages:
            metrics["focus_comparison"] = {
                "best_coverage": max(coverages, key=coverages.get),
                "worst_coverage": min(coverages, key=coverages.get),
                "coverage_range": max(coverages.values()) - min(coverages.values())
            }
        
        # Error rate
        error_count = sum(1 for eval_data in evaluations.values() 
                         if eval_data.get("has_error", False))
        metrics["error_rate"] = error_count / len(evaluations) if evaluations else 0
        
        return metrics
    
    def generate_summary_report(self, all_comparisons):
        """Generate a summary report across all scenarios"""
        report = {
            "total_scenarios": len(all_comparisons),
            "timestamp": datetime.now().isoformat(),
            "method_performance": {},
            "domain_analysis": {},
            "overall_insights": []
        }
        
        # Aggregate method performance
        methods = set()
        for comparison in all_comparisons:
            methods.update(comparison["evaluations"].keys())
        
        for method in methods:
            method_data = []
            for comparison in all_comparisons:
                if method in comparison["evaluations"]:
                    method_data.append(comparison["evaluations"][method])
            
            if method_data:
                report["method_performance"][method] = {
                    "total_runs": len(method_data),
                    "error_rate": sum(1 for d in method_data if d.get("has_error", False)) / len(method_data),
                    "avg_response_length": sum(d.get("response_length", 0) for d in method_data) / len(method_data),
                    "avg_focus_coverage": sum(d.get("focus_coverage", 0) for d in method_data) / len(method_data)
                }
        
        return report
