# Prompt - Frontend Refactor

다음 기존 모니터링 화면 코드를 디자인 시스템 기준으로 리팩토링해줘.

## 입력

- 기존 화면 코드
- Token CSS
- Component spec
- Bug report

## 리팩토링 목표

1. 하드코딩된 색상, 간격, 폰트를 토큰으로 치환
2. Stage / state 표시 체계를 명확히 분리
3. Group board를 2x2 카드 + group paging + internal scroll 구조로 변경
4. 상시 detail panel 구조 유지
5. 중복 데이터 제거
6. abort, polling, completed plan refresh 관련 버그를 화면에서 드러나게 수정

## 출력 요청

- 변경 전 문제 요약
- 변경 후 컴포넌트 구조
- 실제 diff 또는 변경 코드
- breaking change 여부
- 회귀 테스트 체크리스트
