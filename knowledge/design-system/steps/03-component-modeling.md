# Step 3. Component Modeling

## 목적

화면 구성요소를 재사용 가능한 컴포넌트 계층으로 나누고, Stitch 정의가 실제 프론트엔드 구조로 이어지게 만든다.

## 권장 컴포넌트 계층

### Atoms

- StatusDot
- StageBadge
- MetricItem
- DeviceCountChip
- OverflowHint
- PagerButton

### Molecules

- MonitorHeader
- GroupSummaryCard
- DeviceCard
- DeviceStateRow
- ErrorListSection

### Organisms

- GroupBoard
- DeviceDetailPanel
- MonitorStagePanel
- MonitorWorkspace

## 이번 화면에서 중요한 설계 포인트

### Stage vs State 분리

- Stage는 상단 흐름 구조다.
- State는 각 디바이스와 그룹, 전체 보드 상태 표현이다.
- 같은 색을 쓰더라도 라벨과 위치가 달라야 한다.

### Group board

- 그룹 자체 탐색은 `Prev` / `Next`
- 그룹 내부 5개 이상 디바이스는 스크롤
- 4개만 보이는 상황에서 추가 장비 존재가 보이도록 `+N more` 또는 scroll hint 제공

### Detail panel

- 우측 상시 영역으로 유지
- 에러 뇌관 목록은 count와 목록이 중복되지 않게 정리
- `NG count`는 이미 다른 정보로 표현되면 중복 제거

## 컴포넌트 명세 템플릿

```md
# DeviceCard

## Role
Group board 내 개별 발파기 상태 요약

## Props
- name
- orderInGroup
- state
- delayTime
- errorSummary
- isSelected

## States
- idle
- progress
- complete
- error

## Do
- 상태를 색과 텍스트 둘 다로 표현한다.
- 상세 패널과 선택 상태를 연동한다.

## Don't
- 그룹 수준 데이터와 디바이스 수준 데이터를 혼합하지 않는다.
```
