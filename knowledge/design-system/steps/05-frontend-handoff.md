# Step 5. Frontend Handoff

## 목적

Stitch에서 정리한 디자인 시스템을 실제 프론트엔드 코드 리팩토링으로 연결한다.

## 인계 순서

1. 화면별 명세서 확정
2. 토큰 JSON 정리
3. CSS custom properties 생성
4. 공통 컴포넌트 생성
5. 화면별 조합 컴포넌트 생성
6. 상태 전이 로직과 UI 연결
7. 버그 리포트 항목 회귀 테스트

## 코드 인계물

- Token source: `json`
- Generated token file: `css`
- Component spec: `md`
- Screen behavior spec: `md`
- Refactor prompt: `md`

## 구현 원칙

- Hardcoded value를 바로 화면에 넣지 않는다.
- 화면 특화 예외는 먼저 공통 컴포넌트로 흡수 가능한지 검토한다.
- Stage와 state enum을 분리한다.
- 상태 표시는 디자인 시스템 토큰에서만 읽는다.

## 권장 디렉터리 예시

```text
src/
  design-system/
    tokens/
    components/
    patterns/
  features/
    monitoring/
      screens/
      state/
      adapters/
```

## 검수 포인트

- 2x2 카드 가시성이 실제 해상도에서 충분한가
- 5개 이상 장비 존재가 즉시 드러나는가
- abort 시 `CANCELED`가 메인 화면에도 반영되는가
- polling 중 누락 데이터가 정상으로 보이는 문제를 방지했는가
