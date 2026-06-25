# IVI 리얼타임 설계 — 소프트 vs 하드, RTOS 분리

> 일반 Android와 IVI 시스템의 실시간성이 근본적으로 다른 이유

## 소프트 vs 하드 리얼타임

```
소프트 리얼타임 (일반 Android):
→ 16ms 안에 렌더링하면 좋음
→ 가끔 놓쳐도 "버벅임"으로 끝남
→ 사용자 불쾌하지만 안전에 무관

하드 리얼타임 (IVI 안전 크리티컬):
→ 특정 시간 내에 반드시 응답
→ 놓치면 = 시스템 실패
→ 에어백 미작동, 브레이크 응답 지연 = 인명 사고
```

---

## IVI 하드 리얼타임 구현 방법

### 1. RTOS 분리

```
┌─────────────────────────────────────┐
│         IVI 하드웨어                 │
│                                     │
│  ┌─────────────┐  ┌───────────────┐ │
│  │   Android   │  │     RTOS      │ │
│  │ (인포테인먼트)│  │ (QNX/AUTOSAR) │ │
│  │ 내비, 음악  │  │  브레이크,    │ │
│  │ 앱스토어    │  │  에어백,      │ │
│  └─────────────┘  │  조향 제어    │ │
│                   └───────────────┘ │
└─────────────────────────────────────┘
```

안전 크리티컬 기능은 QNX, AUTOSAR 같은 RTOS가 담당.  
Android는 인포테인먼트(편의 기능) 레이어만 담당.

### 2. AAOS 레이어 분리

```
AAOS:
├── 인포테인먼트 레이어  ← Android 담당
│   └── 내비, 음악, 앱
│
└── 차량 제어 레이어    ← CarPropertyManager로만 접근
    └── 속도, 기어, HVAC
        (실제 제어는 RTOS/ECU 담당)
```

Android 앱이 CarPropertyManager로 차량 데이터를 읽을 수 있지만  
**실제 브레이크/조향을 Android가 직접 제어하지 않음.**  
그 아래에 RTOS/ECU가 따로 존재.

### 3. CarWatchdog — ANR과 다른 강제 재시작

```kotlin
// 일반 Android ANR: 다이얼로그 띄우고 기다림
// IVI Watchdog: 강제 재시작

carWatchdogManager.registerClient(
    client,
    CarWatchdogManager.TIMEOUT_CRITICAL // 3초
)

// 앱은 주기적으로 살아있음을 알려야 함
carWatchdogManager.tellClientAlive(client, sessionId)
// 못 보내면 → 강제 재시작
```

### 4. 안전 표준 — ISO 26262 ASIL

```
ASIL A → 낮은 위험 (실내 조명)
ASIL B → 중간 (와이퍼)
ASIL C → 높음 (조향 보조)
ASIL D → 최고 위험 (에어백, 브레이크)
```

ASIL D: 소프트웨어 결함률 **10^-8/시간** 이하 요구.  
Android로는 충족 어려움 → RTOS가 담당하는 이유.

---

## 핵심 인사이트

> CarPropertyManager가 존재하는 이유:
> Android가 차량 데이터에 접근하되,
> 실제 안전 크리티컬 제어는 건드리지 못하게
> 경계를 API로 강제하는 구조.
>
> IVI 플랫폼 엔지니어의 핵심 역할:
> "Android 레이어와 RTOS 레이어를 어떻게 나눌 것인가"

## 관련 개념
- QNX, AUTOSAR
- ISO 26262, ASIL
- CarPropertyManager, CarWatchdogManager
- ECU (Electronic Control Unit)
- AAOS (Android Automotive OS)

---
*2026-06-24*
