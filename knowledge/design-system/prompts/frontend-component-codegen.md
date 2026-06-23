# Prompt - Frontend Component Codegen

다음 디자인 시스템 명세를 기반으로 React + TypeScript 컴포넌트를 생성해줘.

## 입력

- Token JSON
- Component spec
- Screen behavior spec

## 요구사항

- CSS custom properties 사용
- inline style 금지
- `className` prop 허용
- 접근성 속성 포함
- Stage와 state enum 분리
- 상태 색상은 semantic token에서만 읽기

## 이번 화면에서 우선 생성할 컴포넌트

- `MonitorHeader`
- `GroupBoard`
- `DeviceCard`
- `DeviceDetailPanel`
- `StageProgress`
- `PagerButton`
- `OverflowHint`

## 추가 규칙

- 좌측 바와 상단 `PREV` 버튼 관련 레이아웃은 수정하지 않는다.
- 2x2 카드 밀도를 깨지 않는다.
- 그룹 내부 스크롤과 그룹 전환 버튼 책임을 분리한다.

## 출력 형식

1. 컴포넌트 파일 구조
2. TypeScript props
3. JSX
4. CSS 토큰 사용 예시
5. 테스트 포인트
