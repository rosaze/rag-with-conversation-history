#!/usr/bin/env python3
"""
RAG Experiment with Real Search API
실제 Tavily 검색 API를 사용한 RAG 실험
"""

import json
import os
from datetime import datetime
from experiments.experiment_runner import ExperimentRunner
from utils.helpers import load_scenarios

def test_with_real_search():
    """실제 검색 API를 사용한 RAG 테스트"""
    print("="*60)
    print("RAG 실험 플랫폼 - 실제 검색 API 테스트")
    print("="*60)
    
    # API 키 설정
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = "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"
    
    if not openai_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    print("✅ OpenAI API 키 확인됨")
    print("✅ Tavily API 키 설정됨")
    
    # 시나리오 로드
    scenarios = load_scenarios()
    if not scenarios:
        print("❌ 시나리오를 불러올 수 없습니다.")
        return
    
    print(f"✅ {len(scenarios)}개 시나리오 로드됨")
    
    # 실험 러너 초기화 (검색 API 포함)
    runner = ExperimentRunner(
        openai_key=openai_key,
        tavily_key=tavily_key,
        search_engine="tavily",
        temperature=0.7,
        max_results=5
    )
    
    print("✅ 실험 러너 초기화 완료 (검색 API 활성화)")
    print()
    
    # 테스트할 시나리오들 (다양한 도메인)
    test_scenarios = [scenarios[0], scenarios[1], scenarios[3]]  # 의료, 기술, 투자
    
    all_results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"{'='*50}")
        print(f"시나리오 {i}/{len(test_scenarios)}: {scenario['domain']}")
        print(f"{'='*50}")
        print(f"질문: {scenario['current_question']}")
        print(f"히스토리: {len(scenario['conversation_history'])}턴")
        print()
        
        scenario_results = {}
        
        # 4가지 방법 비교
        methods = [
            ("D1", "LLM만 (히스토리 없음)"),
            ("D2", "LLM + 히스토리"),
            ("D3", "RAG (현재 질문만)"),
            ("D4", "RAG + 히스토리")
        ]
        
        for method_code, method_name in methods:
            print(f"🔄 {method_name} 실행 중...")
            
            try:
                if method_code == "D1":
                    result = runner.run_d1(scenario['current_question'])
                elif method_code == "D2":
                    result = runner.run_d2(scenario['conversation_history'], scenario['current_question'])
                elif method_code == "D3":
                    result = runner.run_d3(scenario['current_question'])
                elif method_code == "D4":
                    result = runner.run_d4(scenario['conversation_history'], scenario['current_question'])
                
                scenario_results[method_code] = result
                
                # 결과 분석
                if 'error' in result:
                    print(f"   ❌ 에러: {result['error']}")
                else:
                    response_length = len(result.get('response', ''))
                    tokens = result.get('usage', {}).get('total_tokens', 'N/A')
                    print(f"   ✅ 성공 - 응답: {response_length}자, 토큰: {tokens}")
                    
                    # 검색 정보 (D3, D4만)
                    if 'search_results' in result:
                        search_count = len(result['search_results'])
                        print(f"   🔍 검색 결과: {search_count}개")
                        
                        if search_count > 0:
                            print(f"   🔍 검색 쿼리: {result.get('search_query', 'N/A')}")
                            # 첫 번째 검색 결과 미리보기
                            first_result = result['search_results'][0]
                            title = first_result.get('title', 'No title')[:50]
                            print(f"   🔍 첫 번째 결과: {title}...")
                        
                        # D4에서 쿼리 개선 확인
                        if method_code == "D4" and 'original_question' in result:
                            original = result['original_question']
                            enhanced = result.get('search_query', '')
                            if original != enhanced:
                                print(f"   🔍 쿼리 개선: {len(original)}자 → {len(enhanced)}자")
            
            except Exception as e:
                print(f"   ❌ 예외: {str(e)}")
                scenario_results[method_code] = {"error": str(e)}
            
            print()
        
        # 응답 품질 비교
        print("📊 응답 비교:")
        for method_code, result in scenario_results.items():
            method_names = {
                "D1": "LLM만",
                "D2": "LLM+히스토리", 
                "D3": "RAG",
                "D4": "RAG+히스토리"
            }
            
            if 'error' not in result:
                response = result.get('response', '')
                search_used = len(result.get('search_results', []))
                
                print(f"  {method_names[method_code]}: {len(response)}자")
                if search_used > 0:
                    print(f"    └ 검색 활용: {search_used}개 결과")
                
                # 응답 미리보기
                preview = response[:80].replace('\n', ' ')
                print(f"    └ 미리보기: {preview}...")
        
        all_results.append({
            "scenario": scenario,
            "results": scenario_results,
            "timestamp": datetime.now().isoformat()
        })
        
        print()
    
    # 전체 결과 분석
    print("="*60)
    print("📈 검색 API 활용 분석")
    print("="*60)
    
    # 검색 활용도 분석
    search_stats = {"D3": [], "D4": []}
    
    for result_set in all_results:
        for method in ["D3", "D4"]:
            if method in result_set["results"] and 'search_results' in result_set["results"][method]:
                search_count = len(result_set["results"][method]['search_results'])
                search_stats[method].append(search_count)
    
    for method, counts in search_stats.items():
        if counts:
            avg_results = sum(counts) / len(counts)
            max_results = max(counts)
            method_name = "RAG (현재 질문만)" if method == "D3" else "RAG + 히스토리"
            print(f"{method_name}:")
            print(f"  평균 검색 결과: {avg_results:.1f}개")
            print(f"  최대 검색 결과: {max_results}개")
    
    # 쿼리 개선 효과 분석
    print(f"\n🔍 쿼리 개선 효과:")
    for result_set in all_results:
        if "D4" in result_set["results"]:
            d4_result = result_set["results"]["D4"]
            if 'original_question' in d4_result and 'search_query' in d4_result:
                original = d4_result['original_question']
                enhanced = d4_result['search_query']
                domain = result_set["scenario"]["domain"]
                
                print(f"  {domain}:")
                print(f"    원래: {original}")
                print(f"    개선: {enhanced}")
                print(f"    길이 변화: {len(original)} → {len(enhanced)}자")
    
    # 결과 저장
    save_search_results(all_results)
    
    print(f"\n{'='*60}")
    print("✅ 실제 검색 API 테스트 완료!")
    print("검색 기능을 통해 RAG의 실제 효과를 확인했습니다.")
    print("="*60)

def save_search_results(results):
    """검색 테스트 결과 저장"""
    try:
        os.makedirs("data", exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/search_test_results_{timestamp}.json"
        
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "search_api_test",
            "total_scenarios": len(results),
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 검색 테스트 결과 저장: {filename}")
        
    except Exception as e:
        print(f"❌ 결과 저장 실패: {e}")

if __name__ == "__main__":
    test_with_real_search()