# Design System Knowledge Base

이 디렉터리는 `Claude -> Google Stitch -> Frontend` 파이프라인을 반복 가능한 작업 방식으로 고정하기 위한 문서 저장소다.

## 목표

- AS-IS / TO-BE 화면 문서를 디자인 시스템 입력 자산으로 변환한다.
- Stitch에서 토큰, 컴포넌트, 화면 구조를 정의한다.
- 정의된 결과를 프론트엔드 코드와 가이드라인으로 연결한다.
- 사람이 매번 설명하지 않아도 되도록 프롬프트와 스크립트로 자동화한다.

## 추천 작업 순서

1. [steps/01-audit-and-spec.md](./steps/01-audit-and-spec.md)
2. [steps/02-stitch-tokenization.md](./steps/02-stitch-tokenization.md)
3. [steps/03-component-modeling.md](./steps/03-component-modeling.md)
4. [steps/04-guidelines-and-rules.md](./steps/04-guidelines-and-rules.md)
5. [steps/05-frontend-handoff.md](./steps/05-frontend-handoff.md)

## 포함 내용

- `steps/`: 단계별 실행 문서
- `prompts/`: Claude, Stitch, Frontend 코드 생성용 프롬프트
- `scripts/`: 토큰 생성, 하드코딩 탐지, 컴포넌트 검수용 보조 스크립트

## 핵심 원칙

- Token First: 값부터 정리하고 컴포넌트는 그 뒤에 만든다.
- Semantic Naming: `red-500`보다 `danger`처럼 의미 기반으로 이름 짓는다.
- Fixed Area Respect: 수정 금지 영역은 화면 규칙으로 문서에 먼저 박아 둔다.
- Screen-to-Code Traceability: 화면 요소가 어떤 컴포넌트와 토큰으로 구현되는지 추적 가능해야 한다.
- Automation-ready: 사람이 이해하는 문장과 기계가 읽는 구조를 함께 남긴다.
