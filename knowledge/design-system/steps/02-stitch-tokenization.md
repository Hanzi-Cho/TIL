# Step 2. Stitch Tokenization

## 목적

화면에서 보이는 색상, 간격, 타이포그래피, 상태 표현을 Stitch와 코드에서 공통으로 쓸 수 있는 토큰으로 치환한다.

## 먼저 결정할 것

- Base spacing unit: `4px`
- Border radius scale
- Typography scale
- Stage / state semantic colors
- Surface / border / text hierarchy

## 이번 프로젝트 기준 토큰 우선순위

### 상태 토큰

- `color.state.idle`
- `color.state.progress`
- `color.state.complete`
- `color.state.error`

### 구조 토큰

- `color.surface.page`
- `color.surface.panel`
- `color.surface.card`
- `color.border.default`
- `color.border.strong`

### 텍스트 토큰

- `color.text.primary`
- `color.text.secondary`
- `color.text.inverse`
- `color.text.status`

### 간격 토큰

- `space.1 = 4`
- `space.2 = 8`
- `space.3 = 12`
- `space.4 = 16`
- `space.5 = 20`
- `space.6 = 24`

## Stitch 입력 팁

- 화면 요소 이름보다 역할 이름으로 토큰을 붙인다.
- `orange` 같은 값 이름보다 `warning`, `accent`, `fixed-nav` 같은 의미 이름을 쓴다.
- 헤더, 그룹 보드, 디바이스 카드, 상세 패널에 같은 토큰을 재사용하게 만든다.

## 결과물 예시

```json
{
  "color": {
    "state": {
      "idle": "#98A2B3",
      "progress": "#F5B301",
      "complete": "#12B76A",
      "error": "#F04438"
    }
  },
  "space": {
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px"
  }
}
```

## 주의할 점

- 색은 많을수록 좋지 않다. 상태색은 네 개만 유지한다.
- Stage와 State를 같은 표현으로 섞지 않는다.
- 고정 영역 색상은 바꾸지 않더라도 토큰 이름으로 참조해야 한다.
