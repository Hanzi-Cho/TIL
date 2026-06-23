# Step 4. Guidelines And Rules

## 목적

디자인 결과물이 예쁜 시안에서 끝나지 않고, 이후 누가 작업해도 같은 기준으로 수정되도록 규칙을 문서화한다.

## 필수 규칙

### Layout rules

- Left bar layout and spacing must remain unchanged.
- Top orange `PREV` button layout and spacing must remain unchanged.
- PC notebook viewing distance를 기준으로 가시성 판단을 한다.
- 상세 패널은 상시 노출 구조를 유지한다.

### Language rules

- 화면 내 사용자 노출 텍스트는 모두 영어로 통일한다.
- 내부 문서에서는 한글 설명을 써도 되지만 UI copy는 영어만 사용한다.

### Data rules

- 중복 정보는 제거한다.
- 그룹 우하단 `NG`처럼 이미 다른 위치에서 전달되는 요약값은 다시 보여주지 않는다.
- `delay time`은 state 맥락에 붙는 데이터이므로 state 열 우측에 배치한다.

### Feedback rules

- 상태는 색상 하나만으로 전달하지 않는다.
- blinking은 현재 진행 중 상태에만 사용한다.
- abort와 error는 모두 빨간 계열을 쓰되 라벨은 구분한다.

## 문서화할 항목

- When to use
- When not to use
- Do / Don't
- Accessibility note
- Fixed area note
- Data dependency note

## 구현 전 점검 질문

- 이 변경이 고정 영역을 건드리는가
- 같은 정보를 두 군데 보여주고 있는가
- 화면 흐름도와 코드 상태머신 이름이 일치하는가
- Stitch 시안과 프론트엔드 컴포넌트 명이 대응되는가
