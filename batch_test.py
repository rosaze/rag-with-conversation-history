#!/usr/bin/env python3
"""
Batch RAG Experiment Test - 전체 시나리오 테스트
교수님 요청에 따른 10개 시나리오 전체 실험
"""

import json
import os
from datetime import datetime
from experiments.experiment_runner import ExperimentRunner
from utils.helpers import load_scenarios

def run_batch_experiment():
    """10개 시나리오 전체 실험 실행"""
    print("="*60)
    print("RAG 실험 플랫폼 - 전체 시나리오 배치 테스트")
    print("="*60)
    
    # API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    print("✅ OpenAI API 키 확인됨")
    
    # 시나리오 로드
    scenarios = load_scenarios()
    print(f"✅ {len(scenarios)}개 시나리오 로드됨")
    
    # 실험 러너 초기화
    runner = ExperimentRunner(
        openai_key=openai_key,
        tavily_key=None,  # 검색 API 없이 테스트
        temperature=0.7
    )
    
    all_results = []
    
    # 각 시나리오별로 실험 실행
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*40}")
        print(f"시나리오 {i}/{len(scenarios)}: {scenario['domain']}")
        print(f"{'='*40}")
        print(f"질문: {scenario['current_question'][:60]}...")
        print(f"히스토리: {len(scenario['conversation_history'])}턴")
        print(f"난이도: {scenario['difficulty']}")
        print(f"맥락 의존도: {scenario['context_dependency']}")
        
        scenario_results = {
            "scenario_id": scenario['id'],
            "domain": scenario['domain'],
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }
        
        # 4가지 방법 실행
        methods = [
            ("D1", "LLM만"),
            ("D2", "LLM+히스토리"), 
            ("D3", "RAG"),
            ("D4", "RAG+히스토리")
        ]
        
        for method_code, method_name in methods:
            print(f"  🔄 {method_name} 실행...")
            
            try:
                if method_code == "D1":
                    result = runner.run_d1(scenario['current_question'])
                elif method_code == "D2":
                    result = runner.run_d2(scenario['conversation_history'], scenario['current_question'])
                elif method_code == "D3":
                    result = runner.run_d3(scenario['current_question'])
                elif method_code == "D4":
                    result = runner.run_d4(scenario['conversation_history'], scenario['current_question'])
                
                scenario_results["results"][method_code] = result
                
                # 간단한 결과 출력
                if 'error' in result:
                    print(f"     ❌ 실패: {result['error'][:50]}...")
                else:
                    response_len = len(result.get('response', ''))
                    tokens = result.get('usage', {}).get('total_tokens', 'N/A')
                    print(f"     ✅ 성공 - {response_len}자, {tokens}토큰")
                    
                    # D4에서 쿼리 개선 확인
                    if method_code == "D4" and 'search_query' in result:
                        original = scenario['current_question']
                        enhanced = result['search_query']
                        if original != enhanced:
                            print(f"     🔍 쿼리 개선됨 (길이: {len(original)} → {len(enhanced)})")
            
            except Exception as e:
                print(f"     ❌ 예외: {str(e)[:50]}...")
                scenario_results["results"][method_code] = {"error": str(e)}
        
        all_results.append(scenario_results)
    
    # 전체 결과 분석
    print(f"\n{'='*60}")
    print("📊 전체 결과 분석")
    print(f"{'='*60}")
    
    # 성공률 계산
    method_stats = {"D1": [], "D2": [], "D3": [], "D4": []}
    
    for result in all_results:
        for method, method_result in result["results"].items():
            success = 'error' not in method_result
            response_len = len(method_result.get('response', '')) if success else 0
            method_stats[method].append({
                'success': success,
                'length': response_len,
                'domain': result['domain']
            })
    
    for method, stats in method_stats.items():
        success_count = sum(1 for s in stats if s['success'])
        success_rate = (success_count / len(stats)) * 100 if stats else 0
        avg_length = sum(s['length'] for s in stats if s['success']) / success_count if success_count > 0 else 0
        
        method_names = {
            "D1": "LLM만 (히스토리 없음)",
            "D2": "LLM + 히스토리", 
            "D3": "RAG (현재 질문만)",
            "D4": "RAG + 히스토리"
        }
        
        print(f"\n[{method_names[method]}]")
        print(f"  성공률: {success_rate:.1f}% ({success_count}/{len(stats)})")
        print(f"  평균 응답 길이: {avg_length:.0f}자")
    
    # 도메인별 성과 분석
    print(f"\n📈 도메인별 성과:")
    domains = set(r['domain'] for r in all_results)
    
    for domain in sorted(domains):
        domain_results = [r for r in all_results if r['domain'] == domain]
        if domain_results:
            result = domain_results[0]
            success_methods = [m for m, mr in result['results'].items() if 'error' not in mr]
            print(f"  {domain}: {len(success_methods)}/4 방법 성공")
    
    # 결과 저장
    save_batch_results(all_results)
    
    print(f"\n{'='*60}")
    print("✅ 전체 배치 테스트 완료!")
    print(f"{'='*60}")

def save_batch_results(results):
    """배치 결과 저장"""
    try:
        os.makedirs("data", exist_ok=True)
        
        batch_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "batch_test",
            "total_scenarios": len(results),
            "results": results
        }
        
        # 파일명에 타임스탬프 포함
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/batch_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 배치 결과 저장됨: {filename}")
        
    except Exception as e:
        print(f"❌ 결과 저장 실패: {e}")

if __name__ == "__main__":
    run_batch_experiment()