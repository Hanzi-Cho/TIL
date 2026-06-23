# Prompt - Stitch Design System Input

다음 모니터링 UI 개편 요구사항을 Stitch에 입력할 수 있도록 디자인 시스템 규칙으로 재정리해줘.

## 제품 맥락

- PC notebook에서 주로 사용
- Controller UI 재사용성과 태블릿 확장 가능성도 고려
- 데모 보드가 아니라 실제 관제 정보 중심 구조

## 수정 금지 영역

- Left sidebar layout, spacing, visual design must remain unchanged.
- Top orange `PREV` button layout, spacing, visual design must remain unchanged.

## 상태 규칙

- Stage: `COMMUNICATION -> ARM -> COMPLETED`
- State colors
  - start: gray
  - in progress: blinking yellow
  - done: green
  - abort or error: red

## 화면 구조 규칙

- Right detail panel is always visible.
- 2x2 device cards sit in the remaining left workspace.
- Group board uses option 3:
  - devices over 4 scroll inside the same group
  - groups switch with `Prev` / `Next`
  - users must notice when more than 4 devices exist

## 데이터 구조 규칙

- Remove duplicated `NG` summary in group board bottom-right.
- Move `delay time` to the right end of the state row.
- Remove duplicated `NG count` beside `error detonators` in the detail panel.
- All UI copy must be English.

## 출력 요청

- Design tokens
- Layout rules
- Component hierarchy
- State display rules
- Accessibility considerations
- Stitch-friendly component descriptions
