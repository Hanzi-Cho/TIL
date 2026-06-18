#!/usr/bin/env python3
import os
import sys
import json
import datetime
import urllib.request
import urllib.error

# Load environment variable key from .env if exists
def load_dotenv(workspace_root):
    env_path = os.path.join(workspace_root, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

def get_api_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def call_gemini_api(api_key, user_input):
    prompt = f"""당신은 개발자의 일일 학습 정리(TIL) 작성을 돕는 전문 AI 어시스턴트입니다.
개발자가 제공한 오늘 한 개발, 역경, 해결 방법 정보를 바탕으로 STAR(Situation & Task, Action, Result, Takeaway) 구조의 TIL 초안을 작성해주세요.
작성 시 다음 요구사항을 엄격히 준수하세요:

1. 구조 스펙 (STAR):
   - Situation & Task (상황 및 문제 정의): 어떤 기능/실험 중 어떤 구체적인 버그/제약 조건이 발생했는지 서술 (단순 요약이 아닌 구체적 서술).
   - Action (원인 분석 및 해결 과정): 문제를 해결하기 위해 시도한 가설들, 분석 방법(예: Memory Profiler 등), 최종 해결책을 채택한 기술적 이유 서술.
   - Result (결과 및 정량적 지표): 해결 후 어떻게 개선되었는지 정량적 지표(예: 메모리 소비량 35% 감소, 수신 실패율 0%)를 포함하여 서술.
   - Takeaway (인사이트): First Principles(기본 물리 법칙/동작 원리) 관점에서 새로 학습하거나 내재화한 점 서술.

2. 톤앤매너:
   - 전문적이고 기술 지향적인 톤앤매너를 유지하세요.
   - 개발자가 캐주얼하게 적은 내용이라도 전문적이고 면접관에게 신뢰감을 주는 어조로 완성도 높게 가다듬어 주세요.

3. 출력 형식:
   - 오직 마크다운 형식으로 작성된 TIL 내용만 출력하고, 불필요한 앞뒤 인사말(예: "네, 준비한 초안입니다")을 절대 포함하지 마세요.

[개발자 제공 입력 정보]
{user_input}
"""

    model_name = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.2
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text = res_data['candidates'][0]['content']['parts'][0]['text']
            return text
    except urllib.error.HTTPError as e:
        print(f"Gemini API Error (HTTP {e.code}): {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode('utf-8')
            print(f"Details: {err_body}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(workspace_root)
    
    api_key = get_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please set the environment variable or create a '.env' file in the workspace root with:", file=sys.stderr)
        print("GEMINI_API_KEY=your_api_key_here", file=sys.stderr)
        sys.exit(1)
        
    user_input = ""
    
    # Check if a file argument is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                user_input = f.read().strip()
            print(f"Read input from file: {file_path}")
        else:
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
    else:
        print("오늘 진행한 개발, 역경/문제, 해결 방법을 텍스트로 자유롭게 입력하세요.")
        print("입력을 마치려면 빈 줄에서 Ctrl+D (Linux/macOS) 또는 Ctrl+Z 후 Enter (Windows)를 누르세요:")
        print("-" * 50)
        try:
            lines = []
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                lines.append(line)
            user_input = "".join(lines).strip()
        except KeyboardInterrupt:
            print("\nInput cancelled.")
            sys.exit(1)
            
    if not user_input:
        print("Error: No input provided.", file=sys.stderr)
        sys.exit(1)
        
    print("\nDrafting TIL using Gemini AI...")
    draft_content = call_gemini_api(api_key, user_input)
    
    # Ensure star directory exists
    star_dir = os.path.join(workspace_root, 'daily')
    if not os.path.exists(star_dir):
        os.makedirs(star_dir)
        
    today = datetime.date.today().strftime('%Y-%m-%d')
    file_path = os.path.join(star_dir, f"{today}.md")
    
    # Format file header if writing new file
    final_content = f"# TIL [{today}] - STAR 기법 적용\n\n{draft_content}"
    
    # If the generated content already has the main title, adjust it
    if draft_content.strip().startswith('#'):
        final_content = draft_content
        
    # Write or overwrite file
    if os.path.exists(file_path):
        print(f"\nWarning: File {file_path} already exists.")
        choice = input("Overwrite? (y/n): ").strip().lower()
        if choice != 'y':
            # Append instead or print to stdout
            print("\nWriting draft to stdout instead:")
            print("=" * 50)
            print(final_content)
            print("=" * 50)
            sys.exit(0)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"\nSuccessfully saved TIL draft to: {file_path}")

if __name__ == '__main__':
    main()
