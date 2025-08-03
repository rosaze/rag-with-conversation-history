#!/usr/bin/env python3
"""
Simple RAG Experiment Test Script
교수님 요청에 따른 간단한 로그 기반 실험 테스트
"""

import json
import os
from datetime import datetime
from experiments.experiment_runner import ExperimentRunner
from utils.helpers import load_scenarios

def run_simple_experiment():
    """간단한 실험 실행"""
    print("="*60)
    print("RAG 실험 플랫폼 - 간단 테스트")
    print("="*60)
    
    # API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   Replit Secrets에서 API 키를 설정해주세요.")
        return
    
    print("✅ OpenAI API 키 확인됨")
    
    # 시나리오 로드
    scenarios = load_scenarios()
    if not scenarios:
        print("❌ 시나리오를 불러올 수 없습니다.")
        return
    
    print(f"✅ {len(scenarios)}개 시나리오 로드됨")
    
    # 실험 러너 초기화 (검색 API 없이)
    runner = ExperimentRunner(
        openai_key=openai_key,
        tavily_key=None,  # 검색 API 없이 테스트
        temperature=0.7
    )
    
    print("✅ 실험 러너 초기화 완료")
    print()
    
    # 첫 번째 시나리오로 테스트
    test_scenario = scenarios[0]
    print(f"📋 테스트 시나리오: #{test_scenario['id']} - {test_scenario['domain']}")
    print(f"   질문: {test_scenario['current_question']}")
    print(f"   히스토리 길이: {len(test_scenario['conversation_history'])}턴")
    print()
    
    # 4가지 방법 테스트
    methods = [
        ("D1: LLM만 (히스토리 없음)", "D1"),
        ("D2: LLM + 히스토리", "D2"), 
        ("D3: RAG (현재 질문만)", "D3"),
        ("D4: RAG + 히스토리", "D4")
    ]
    
    results = {}
    
    for method_name, method_code in methods:
        print(f"🔄 {method_name} 실행 중...")
        
        try:
            if method_code == "D1":
                result = runner.run_d1(test_scenario['current_question'])
            elif method_code == "D2":
                result = runner.run_d2(test_scenario['conversation_history'], test_scenario['current_question'])
            elif method_code == "D3":
                result = runner.run_d3(test_scenario['current_question'])
            elif method_code == "D4":
                result = runner.run_d4(test_scenario['conversation_history'], test_scenario['current_question'])
            
            results[method_code] = result
            
            # 결과 요약 출력
            if 'error' in result:
                print(f"   ❌ 에러: {result['error']}")
            else:
                response_length = len(result.get('response', ''))
                print(f"   ✅ 성공 - 응답 길이: {response_length}자")
                
                # 토큰 사용량 출력
                if 'usage' in result:
                    usage = result['usage']
                    print(f"   📊 토큰 사용: {usage.get('total_tokens', 'N/A')} (입력: {usage.get('prompt_tokens', 'N/A')}, 출력: {usage.get('completion_tokens', 'N/A')})")
                
                # 검색 정보 출력 (있는 경우)
                if 'search_results' in result:
                    search_count = len(result['search_results'])
                    print(f"   🔍 검색 결과: {search_count}개")
                    if 'search_query' in result:
                        print(f"   🔍 검색 쿼리: {result['search_query']}")
        
        except Exception as e:
            print(f"   ❌ 예외 발생: {str(e)}")
            results[method_code] = {"error": str(e)}
        
        print()
    
    # 결과 비교 출력
    print("="*60)
    print("📊 결과 비교")
    print("="*60)
    
    for method_code, result in results.items():
        method_names = {
            "D1": "LLM만 (히스토리 없음)",
            "D2": "LLM + 히스토리", 
            "D3": "RAG (현재 질문만)",
            "D4": "RAG + 히스토리"
        }
        
        print(f"\n[{method_names[method_code]}]")
        
        if 'error' in result:
            print(f"❌ 실패: {result['error']}")
        else:
            response = result.get('response', '')
            print(f"응답 미리보기: {response[:100]}...")
            print(f"응답 길이: {len(response)}자")
            
            if 'search_query' in result and result['search_query'] != test_scenario['current_question']:
                print(f"검색 쿼리 개선: {result['search_query']}")
    
    # 결과 저장
    save_simple_results(test_scenario, results)
    
    print("\n" + "="*60)
    print("✅ 간단 테스트 완료!")
    print("="*60)

def save_simple_results(scenario, results):
    """간단한 결과 저장"""
    try:
        os.makedirs("data", exist_ok=True)
        
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "simple_test",
            "scenario": {
                "id": scenario['id'],
                "domain": scenario['domain'],
                "question": scenario['current_question'],
                "history_length": len(scenario['conversation_history'])
            },
            "results": results
        }
        
        # 기존 결과에 추가
        results_file = "data/simple_test_results.json"
        existing_results = []
        
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
            except:
                existing_results = []
        
        existing_results.append(result_data)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(existing_results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 결과 저장됨: {results_file}")
        
    except Exception as e:
        print(f"❌ 결과 저장 실패: {e}")

if __name__ == "__main__":
    run_simple_experiment()