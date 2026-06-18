#!/usr/bin/env python3
import os
import datetime

def main():
    # Get workspace root
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    star_dir = os.path.join(workspace_root, 'daily')
    
    # Create star directory if not exists
    if not os.path.exists(star_dir):
        os.makedirs(star_dir)
        print(f"Created directory: {star_dir}")
        
    # Get today's date
    today = datetime.date.today().strftime('%Y-%m-%d')
    file_path = os.path.join(star_dir, f"{today}.md")
    
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return
        
    # Write template
    template_content = f"""# TIL [{today}] - STAR 기법 적용

## Situation & Task (상황 및 문제 정의)
* 어떤 기능/실험을 하다가 어떤 버그나 제약 조건이 발생했는가?
* 예: [Zebra PDA 기기에서 BLE 데이터를 연속 수신할 때 백그라운드 스레드 정체로 인해 OOM(Out Of Memory) 에러 발생]

## Action (원인 분석 및 해결 과정)
* 문제를 해결하기 위해 시도한 가설들과 덤프 분석 기법 (예: Memory Profiler 추적 결과)
* 선택한 해결책과 그 이유 (예: Coroutine Flow Backpressure 제어 및 Dispatcher 최적화)

## Result (결과 및 정량적 지표)
* 해결 후 어떻게 개선되었는가? (예: 메모리 소비량 35% 감소, 수신 실패율 0%)

## Takeaway (인사이트)
* 이 기술의 내부 동작 원리(First Principles)에 대해 새로 알게 된 점
"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
        
    print(f"Successfully created template: {file_path}")

if __name__ == '__main__':
    main()
