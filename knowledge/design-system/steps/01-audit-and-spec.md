# Step 1. Audit And Spec

## 목적

PPT, 스크린샷, 버그 리포트, 화면 흐름도를 프론트엔드 설계에 바로 연결할 수 있는 구조화된 명세로 바꾼다.

## 입력물

- AS-IS 화면 스크린샷
- TO-BE 요구사항
- 상태 전이 시나리오
- 버그 리포트
- 수정 금지 규칙

## 산출물

- 화면별 명세서
- 화면 흐름도
- 구성요소 목록
- 디자인 시스템 입력용 요약본

## 정리 기준

### 1. 화면 메타데이터

- Screen name
- Stage
- Main state
- Trigger
- Success condition
- Abort / error condition

### 2. 고정 규칙

- Left navigation bar is fixed and must not be redesigned.
- Top orange `PREV` button is fixed and must not be redesigned.
- 화면 텍스트는 모두 영어로 통일한다.
- 우측 상세 패널은 확장형이 아니라 상시 노출 영역으로 유지한다.

### 3. 상태 체계

- Stage: `COMMUNICATION -> ARM -> COMPLETED`
- State colors
  - idle: gray
  - in-progress: blinking yellow
  - done: green
  - aborted-or-error: red

### 4. 그룹 보드 규칙

- 기본 2x2 카드 뷰를 유지한다.
- 4개를 초과하면 그룹 내부는 세로 스크롤로 더 본다.
- 사용자가 5개 이상 존재를 놓치지 않도록 overflow 표시를 반드시 넣는다.
- 그룹 간 이동은 `Prev` / `Next` 버튼으로 한다.

## 화면 문서 템플릿

```md
# [Screen Name]

## 1. Required Elements
- Header:
- Group board:
- Device card:
- Detail panel:

## 2. Fixed Rules
- Must preserve:
- Must not change:

## 3. Behavior
- Enter condition:
- Main interactions:
- State transitions:
- Error / abort behavior:

## 4. Implementation Intent
- Why this layout:
- Why this component split:
- Why this status rule:
```

## 체크리스트

- AS-IS와 TO-BE를 같은 용어 체계로 비교했는가
- 버그가 화면 요소 단위로 매핑되었는가
- 수정 금지 영역이 문서에 명시되었는가
- Stitch에 넣을 때 빠질 정보가 없는가
