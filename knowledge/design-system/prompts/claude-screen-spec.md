# Prompt - Claude Screen Spec

다음 모니터링 기능 재설계 자료를 바탕으로 화면별 명세서를 작성해줘.

## 입력 자료

- AS-IS 스크린샷
- TO-BE 요구사항
- 상태 전이 시나리오
- 버그 리포트

## 반드시 지킬 규칙

- 화면별로 아래 4개 섹션을 순서대로 작성
  1. Screen Screenshot
  2. Required Elements And Intent
  3. Behavior And Screen Name
  4. Screen Flow
- AS-IS와 TO-BE 모두 실제 관제 화면 기준으로 설명
- 좌측 바와 상단의 주황색 `PREV` 버튼은 상위 레이어 고정 영역이며 수정 금지라고 명시
- 화면 텍스트는 영어 기준으로 작성
- Stage는 `COMMUNICATION -> ARM -> COMPLETED`
- State color는 아래 네 개만 사용
  - gray: start
  - blinking yellow: in progress
  - green: done
  - red: abort or error

## 그룹 보드 규칙

- 2x2 디바이스 카드 크기 유지
- 5개 이상은 그룹 내부 스크롤
- 다른 그룹은 `Prev` / `Next` 버튼으로 이동
- 사용자가 추가 장비 존재를 놓치지 않도록 overflow 신호를 반드시 설계

## 출력 형식

```md
# [Screen Name]

## 1. Screen Screenshot
- ...

## 2. Required Elements And Intent
- ...

## 3. Behavior And Screen Name
- ...

## 4. Screen Flow
- ...
```
