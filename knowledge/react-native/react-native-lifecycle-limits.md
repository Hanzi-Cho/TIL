# React Native 생명주기 한계와 네이티브 의존성

> RN 생명주기 관리 부재가 백그라운드 처리, Foreground Service, 메모리 관리에 미치는 영향

## 네이티브 vs RN 생명주기 제어 비교

```
Android 네이티브                React Native
────────────────                ────────────
Activity.onStop()         →     AppState 'background' (뭉뚱그려짐)
Activity.onDestroy()      →     컴포넌트 unmount (보장 안 됨)
ViewModel.onCleared()     →     없음 (직접 구현)
Service.onStartCommand()  →     Headless JS (제약 많음)
onTrimMemory(level)       →     없음 (레벨 구분 불가)
```

네이티브는 세밀한 타이밍에 콜백이 오지만, RN은 뭉뚱그려진 이벤트만 받는다.

---

## 1. 백그라운드 처리

```javascript
AppState.addEventListener('change', (state) => {
    if (state === 'background') {
        // JS 엔진이 언제 멈출지 보장 없음
    }
});
```

- 백그라운드에서 긴 작업(다운로드, 위치 추적)은 **네이티브 모듈 직접 작성 필요**
- 순수 JS로는 불가능

## 2. Foreground Service 선언

RN에서 Foreground Service를 제대로 쓰려면:

```
1. 네이티브 모듈 작성 (Kotlin/Java)
2. AndroidManifest에 Service 선언
3. JS에서 NativeModule 호출
```

`react-native-foreground-service` 같은 라이브러리가 이 네이티브 코드를 대신 작성해주는 것.  
순수 RN 레이어에서 해결 불가.

## 3. 메모리 관리

```javascript
// onTrimMemory 레벨 구분 불가
// 백그라운드 진입 여부만 감지 가능
AppState.addEventListener('change', (state) => {
    if (state === 'background') {
        imageCache.clear(); // 무조건 클리어 (단계적 대응 불가)
    }
});
```

- 네이티브: 메모리 압박 수준에 따라 단계적 캐시 해제 가능
- RN: **전부 or 아무것도 안 함** 수준만 가능

---

## 기능별 비교표

| 기능 | 네이티브 | RN |
|---|---|---|
| 생명주기 세밀한 제어 | O | X (뭉뚱그려짐) |
| 백그라운드 긴 작업 | Service로 가능 | 네이티브 모듈 필요 |
| Foreground Service | 직접 선언 | 네이티브 모듈 필요 |
| 메모리 단계별 대응 | onTrimMemory | 레벨 구분 불가 |
| ViewModel 자동관리 | O | X (직접 설계) |

---

## 핵심 인사이트

> RN은 "빠르게 앱을 만드는 프레임워크"이지
> "플랫폼을 제어하는 도구"가 아니다.
>
> 플랫폼 레이어에 가까운 작업일수록 RN 추상화가 얇아지고
> 결국 네이티브 코드가 필요해진다.
>
> RN 앱에서 성능/메모리 이슈가 생겼을 때
> 네이티브를 모르면 근본 해결이 안 되는 이유.
>
> **런처 개발 프로젝트 사례의 교훈 (2026-06-25):**
> 적은 개발 인력 하에 트럭 카운트(Bus Factor) 및 관리 포인트를 최소화하기 위해 기술 스택을 React 계열로 통일하더라도, 안정성이 향상되고 아키텍처에 대한 이해가 깊어질수록 `Native - Bridge - React` 레이어 간의 명확한 경계 구분과 직접적인 생명 주기 관리, 그리고 엄격한 상태 머신의 정의 필요성으로 인해 오히려 플랫폼 레이어 개발의 복잡도가 크게 증가한다.

## 관련 개념
- Headless JS Task
- NativeModule, TurboModule (New Architecture)
- AppState, InteractionManager
- react-native-foreground-service

---
*2026-06-24*
