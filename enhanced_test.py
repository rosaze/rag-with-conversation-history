#!/usr/bin/env python3
"""
Enhanced RAG Experiment with Quality Evaluation

This module provides comprehensive quality assessment for RAG experiments,
comparing four different approaches: LLM-only, LLM+history, RAG, and RAG+history.
"""

import json
import os
from datetime import datetime
from experiments.experiment_runner import ExperimentRunner
from src.evaluator import ResponseEvaluator
from src.llm_handler import LLMHandler

def load_scenarios():
    """Load test scenarios from JSON file"""
    with open('data/scenarios.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('scenarios', [])

def evaluate_response_quality(response, domain, question):
    """Evaluate response quality using domain-specific criteria"""
    quality_metrics = {
        "relevance_score": 0,
        "completeness_score": 0, 
        "specificity_score": 0,
        "practical_value": 0
    }
    
    response_lower = response.lower()
    
    # Domain-specific quality criteria
    domain_criteria = {
        "의료상담": {
            "relevant_terms": ["증상", "치료", "운동", "생활습관", "근력", "체중", "스트레칭", "관절"],
            "specific_terms": ["대퇴사두근", "연골", "무릎", "물리치료", "냉찜질", "온찜질"],
            "practical_terms": ["방법", "운동법", "주의사항", "단계별", "일상"]
        },
        "기술지원": {
            "relevant_terms": ["오류", "해결", "설치", "설정", "코드", "버전", "시스템"],
            "specific_terms": ["dockerfile", "_ctypes", "python", "pip", "flask", "gunicorn"],
            "practical_terms": ["해결법", "단계", "명령어", "방법", "설정"]
        },
        "투자상담": {
            "relevant_terms": ["투자", "포트폴리오", "분산", "수익", "위험", "자산", "펀드"],
            "specific_terms": ["etf", "국내주식", "해외주식", "채권", "리밸런싱", "목표"], 
            "practical_terms": ["비율", "방법", "전략", "계획", "단계"]
        }
    }
    
    criteria = domain_criteria.get(domain, domain_criteria["의료상담"])
    
    # 관련성 점수 (0-10)
    relevant_count = sum(1 for term in criteria["relevant_terms"] if term in response_lower)
    quality_metrics["relevance_score"] = min(10, relevant_count * 1.5)
    
    # 구체성 점수 (0-10)  
    specific_count = sum(1 for term in criteria["specific_terms"] if term in response_lower)
    quality_metrics["specificity_score"] = min(10, specific_count * 2)
    
    # 실용성 점수 (0-10)
    practical_count = sum(1 for term in criteria["practical_terms"] if term in response_lower)
    quality_metrics["practical_value"] = min(10, practical_count * 2)
    
    # 완성도 점수 (응답 길이 및 구조 기반)
    word_count = len(response.split())
    has_structure = "1." in response or "**" in response or "###" in response
    quality_metrics["completeness_score"] = min(10, (word_count / 50) + (3 if has_structure else 0))
    
    # 전체 품질 점수
    total_score = sum(quality_metrics.values()) / 4
    quality_metrics["overall_quality"] = round(total_score, 2)
    
    return quality_metrics

def run_enhanced_experiment():
    """Run comprehensive experiment with quality evaluation"""
    print("=" * 60)
    print("RAG 실험 플랫폼 - 품질 중심 평가")
    print("=" * 60)
    
    # API 키 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        return
    
    print("✅ OpenAI API 키 확인됨")
    
    if tavily_key:
        print("✅ Tavily API 키 설정됨 - RAG 기능 활성화")
        search_enabled = True
    else:
        print("⚠️  Tavily API 키 없음 - 검색 없는 RAG 테스트")
        search_enabled = False
    
    # 시나리오 로드
    scenarios = load_scenarios()
    print(f"✅ {len(scenarios)}개 시나리오 로드됨")
    
    # 실험 러너 초기화
    runner = ExperimentRunner(
        openai_key=openai_key,
        tavily_key=tavily_key if search_enabled else None
    )
    print("✅ 실험 러너 초기화 완료")
    
    results = []
    
    # 첫 3개 시나리오로 테스트
    test_scenarios = scenarios[:3]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*50}")
        print(f"시나리오 {i}/{len(test_scenarios)}: {scenario['domain']}")
        print(f"{'='*50}")
        print(f"질문: {scenario['current_question']}")
        print(f"히스토리: {len(scenario.get('conversation_history', []))}턴")
        
        # 4가지 방법으로 실험 실행
        experiment_results = runner.run_all_methods(scenario)
        
        # 품질 평가 추가
        quality_analysis = {}
        response_comparison = {}
        
        for method, result in experiment_results.items():
            if 'response' in result:
                # 품질 평가
                quality_metrics = evaluate_response_quality(
                    result['response'], 
                    scenario['domain'], 
                    scenario['current_question']
                )
                quality_analysis[method] = quality_metrics
                
                # 응답 비교를 위한 요약
                response_preview = result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
                
                response_comparison[method] = {
                    "length": len(result['response']),
                    "preview": response_preview,
                    "quality_score": quality_metrics["overall_quality"],
                    "tokens": result.get('usage', {}).get('total_tokens', 0),
                    "search_results": len(result.get('search_results', [])),
                    "has_search": len(result.get('search_results', [])) > 0
                }
                
                print(f"\n🔄 {method} 완료:")
                print(f"   품질점수: {quality_metrics['overall_quality']}/10")
                print(f"   응답길이: {len(result['response'])}자")
                print(f"   토큰사용: {result.get('usage', {}).get('total_tokens', 0)}개")
                if result.get('search_results'):
                    print(f"   검색결과: {len(result['search_results'])}개")
        
        # 결과 저장
        scenario_result = {
            "scenario_id": scenario["id"],
            "domain": scenario["domain"],
            "question": scenario["current_question"],
            "timestamp": datetime.now().isoformat(),
            "experiment_results": experiment_results,
            "quality_analysis": quality_analysis,
            "response_comparison": response_comparison
        }
        
        results.append(scenario_result)
        
        # 시나리오별 품질 비교 출력
        print(f"\n📊 품질 비교 결과:")
        methods = ["D1", "D2", "D3", "D4"]
        method_names = ["LLM만", "LLM+히스토리", "RAG", "RAG+히스토리"]
        
        for method, name in zip(methods, method_names):
            if method in quality_analysis:
                quality = quality_analysis[method]
                comparison = response_comparison[method]
                print(f"  {name}: {quality['overall_quality']}/10점")
                print(f"    └ 관련성:{quality['relevance_score']:.1f} 구체성:{quality['specificity_score']:.1f} 실용성:{quality['practical_value']:.1f}")
                if comparison['has_search']:
                    print(f"    └ 검색 활용: {comparison['search_results']}개 결과")
    
    # 전체 결과 분석
    print(f"\n{'='*60}")
    print("📈 전체 실험 결과 분석")
    print(f"{'='*60}")
    
    # 방법별 평균 품질 점수
    method_averages = {}
    for method in ["D1", "D2", "D3", "D4"]:
        scores = []
        for result in results:
            if method in result["quality_analysis"]:
                scores.append(result["quality_analysis"][method]["overall_quality"])
        if scores:
            method_averages[method] = sum(scores) / len(scores)
    
    method_names = {
        "D1": "LLM만 (히스토리 없음)",
        "D2": "LLM + 히스토리", 
        "D3": "RAG (현재 질문만)",
        "D4": "RAG + 히스토리"
    }
    
    print("🏆 방법별 평균 품질 점수:")
    for method, avg_score in sorted(method_averages.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method_names[method]}: {avg_score:.2f}/10점")
    
    # 가설 검증
    print(f"\n🔬 가설 검증 결과:")
    if "D3" in method_averages and "D1" in method_averages:
        h1_result = method_averages["D3"] > method_averages["D1"]
        print(f"  H1 (RAG > LLM-only): {'✅ 검증됨' if h1_result else '❌ 기각됨'}")
        print(f"    RAG: {method_averages.get('D3', 0):.2f} vs LLM-only: {method_averages.get('D1', 0):.2f}")
    
    if "D4" in method_averages and "D3" in method_averages:
        h2_result = method_averages["D4"] > method_averages["D3"]
        print(f"  H2 (히스토리 반영 > 단순): {'✅ 검증됨' if h2_result else '❌ 기각됨'}")
        print(f"    RAG+히스토리: {method_averages.get('D4', 0):.2f} vs RAG: {method_averages.get('D3', 0):.2f}")
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/enhanced_test_results_{timestamp}.json"
    
    final_results = {
        "experiment_type": "enhanced_quality_evaluation",
        "timestamp": datetime.now().isoformat(),
        "total_scenarios": len(results),
        "search_enabled": search_enabled,
        "method_averages": method_averages,
        "hypothesis_results": {
            "H1_RAG_better_than_LLM": method_averages.get("D3", 0) > method_averages.get("D1", 0),
            "H2_history_better_than_simple": method_averages.get("D4", 0) > method_averages.get("D3", 0)
        },
        "detailed_results": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"📁 결과 저장됨: {output_file}")
    
    print(f"\n{'='*60}")
    print("✅ 향상된 품질 평가 실험 완료!")
    print("이제 교수님께 의미 있는 연구 결과를 보고할 수 있습니다.")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_enhanced_experiment()