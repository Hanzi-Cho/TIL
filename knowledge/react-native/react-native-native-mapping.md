# React Native — Android 네이티브 개념 매핑

> RN에서 쓰는 개념들이 Android 네이티브 레이어에서 어떻게 동작하는가

## RN 스레드 구조

```
┌─────────────────────────────────────────────┐
│              React Native App               │
│                                             │
│  JS Thread          Shadow Thread           │
│  (JS 엔진 실행)      (레이아웃 계산)          │
│       │                   │                 │
│       └──────┬────────────┘                 │
│           Bridge / JSI                      │
│              │                              │
│  Main Thread (UI Thread)                    │
│  Native Modules Thread                      │
└─────────────────────────────────────────────┘
```

### JS Thread
- JavaScript 코드 실행 (React 렌더링 로직, 비즈니스 로직)
- Android의 백그라운드 스레드에 해당
- Hermes / V8 엔진이 여기서 돌아감
- **메인 스레드가 아님** → UI 직접 접근 불가

### Shadow Thread
- Yoga 레이아웃 엔진으로 UI 레이아웃 계산
- Android의 measure/layout 패스에 해당
- JS Thread와 Main Thread 사이 중간 계산 담당

### Main Thread (UI Thread)
- Android 네이티브 메인 스레드와 동일
- Looper/Handler/MessageQueue 구조 그대로
- 실제 View 렌더링은 여기서만 가능

### Native Modules Thread
- 카메라, 파일, DB 등 네이티브 모듈 실행
- Android의 `Dispatchers.IO` 스레드풀에 해당

---

## Bridge vs JSI

### Old Architecture (Bridge)
```
JS Thread  →  JSON 직렬화  →  Bridge  →  역직렬화  →  Main Thread
```
- 비동기, 직렬화 오버헤드 큼
- Android Binder IPC와 유사한 구조 (경계를 넘을 때 직렬화)

### New Architecture (JSI, 2022+)
```
JS Thread  →  JSI (C++ 레이어)  →  Main Thread
             (직접 메모리 참조)
```
- 동기 호출 가능, 직렬화 오버헤드 없음
- Android Binder의 mmap(1회 복사) 개선과 같은 방향의 발전

---

## 네이티브 개념 매핑표

| Android 네이티브 | React Native | 비고 |
|---|---|---|
| Main Thread / Looper | Main Thread (UI Thread) | 동일한 Android 메인 스레드 |
| Handler.post() | runOnUiThread / Bridge 메시지 | JS→Native 전달 방식 |
| Dispatchers.IO | Native Modules Thread | 네이티브 모듈 실행 |
| Dispatchers.Default | JS Thread | JS 엔진 연산 |
| ViewModel | Zustand / Redux store | 생명주기 관리 방식 다름 |
| SavedStateHandle | AsyncStorage / MMKV | 영속화 레이어 |
| Lifecycle (ON_START 등) | AppState, useEffect cleanup | JS 레벨 생명주기 |
| Foreground Service | Headless JS Task | 백그라운드 실행 |
| LMK | OS 레벨 (RN이 개입 불가) | 동일하게 적용됨 |
| onTrimMemory() | 직접 콜백 없음 | NativeEventEmitter로 간접 수신 가능 |

---

## 각 개념 상세

### Looper/Handler → RN에서는?

```javascript
// JS Thread에서 Main Thread로 작업 전달
// Android: handler.post { updateUI() }
// RN 동일 효과:
InteractionManager.runAfterInteractions(() => {
    // 애니메이션/인터랙션 완료 후 실행 (메인 스레드)
});

// 또는
requestAnimationFrame(() => {
    // 다음 프레임에 실행
});
```

### Dispatcher → RN에서는?

```javascript
// Dispatchers.IO 해당 — 네이티브 모듈이 자동으로 별도 스레드 처리
const data = await AsyncStorage.getItem('key'); // 내부적으로 IO 스레드

// Dispatchers.Main 해당 — setState는 항상 JS Thread → Main Thread 경유
setState({ count: 1 }); // Bridge/JSI 통해 Main Thread에서 렌더링
```

### ViewModel 생명주기 → RN에서는?

```
Android ViewModel          React Native
─────────────────          ────────────────
Activity/Fragment          Screen 컴포넌트
생명주기에 묶임             마운트/언마운트에 묶임

navGraphViewModels()       Navigation state (React Navigation)
SavedStateHandle           AsyncStorage / MMKV 직접 관리
```

RN은 ViewModel 같은 플랫폼 제공 생명주기 컨테이너가 없어서 **개발자가 직접 설계**해야 해요.

### Foreground Service → RN에서는?

```javascript
// Headless JS Task — 앱이 백그라운드일 때 JS 코드 실행
// Android 네이티브 Foreground Service 위에서 동작
AppRegistry.registerHeadlessTask('SyncTask', () => SyncTask);
```

내부적으로는 Android Foreground Service가 동작하고, 그 위에서 JS를 실행하는 구조예요. 알림 노출 등 제약은 동일하게 적용.

### LMK / onTrimMemory → RN에서는?

```javascript
// onTrimMemory 직접 콜백 없음
// AppState로 포그라운드/백그라운드 전환만 감지 가능
AppState.addEventListener('change', (state) => {
    if (state === 'background') {
        // 캐시 정리 등 — onTrimMemory TRIM_MEMORY_UI_HIDDEN에 해당
    }
});
```

LMK는 RN도 동일하게 적용. JS 레벨에서 막을 방법 없음.

---

## 핵심 인사이트

> React Native는 Android 네이티브 위에 JS 레이어를 올린 구조.
> 네이티브 개념(Looper, LMK, Foreground Service)은 그대로 적용되고,
> RN이 추상화 레이어를 제공할 뿐이다.
>
> 네이티브를 모르면 RN의 성능 문제를 근본적으로 해결할 수 없다.

## 관련 개념
- Hermes Engine, JSI, Fabric (New Architecture)
- React Navigation, Zustand, MMKV
- Android Binder IPC, Looper/Handler

---
*2026-06-24*
