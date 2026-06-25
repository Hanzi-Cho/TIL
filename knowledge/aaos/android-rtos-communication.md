# Android ↔ RTOS 통신 구조

> Android에서 RTOS로 크리티컬한 명령을 전달할 때 실시간성은 누가 보장하는가

## 통신 경로

```
Android (AAOS)
    │
    │  HAL (Hardware Abstraction Layer)
    │  ↕ AIDL / HIDL
    │
Vehicle HAL (VHAL)
    │
    │  CAN Bus / LIN Bus / Ethernet
    │
RTOS / ECU
```

Android가 RTOS와 직접 통신하지 않는다.  
**VHAL(Vehicle HAL)이 중간에서 중재.**

---

## VHAL 역할

```kotlin
// Android 앱
carPropertyManager.setProperty(
    CarPropertyConfig.VEHICLE_PROPERTY_HVAC_TEMPERATURE,
    VehicleAreaSeat.SEAT_ROW_1_LEFT,
    22.5f
)
// → VHAL → CAN Bus → HVAC ECU (RTOS)
```

앱은 CarPropertyManager에 값을 쓰고,  
VHAL이 CAN 메시지로 변환해서 ECU에 전달.

---

## CAN Bus가 실시간성을 보장하는 방법

```
CAN Bus 특성:
- 우선순위 기반 중재
- 브레이크 메시지 > 에어컨 메시지
- 전송 지연 수 마이크로초 단위
- Android가 개입할 수 없는 하드웨어 레벨
```

크리티컬 경로의 실시간성은 **Android가 아닌 CAN Bus + ECU(RTOS)가 보장.**

---

## Android가 할 수 있는 것

VHAL까지 최대한 빠르게 전달하는 것.

```kotlin
// 고우선순위 스레드로 VHAL에 전달
val vehicleThread = HandlerThread(
    "VehicleThread",
    Process.THREAD_PRIORITY_URGENT_AUDIO
)
vehicleThread.start()

val vehicleHandler = Handler(vehicleThread.looper)
vehicleHandler.post {
    vhal.set(property, value) // 최대한 빠르게 VHAL에 전달
}
```

---

## 레이어별 책임 분리

| 레이어 | 실시간성 보장 주체 |
|---|---|
| Android 앱 | ❌ 소프트 리얼타임 |
| VHAL | △ 최대한 빠르게 전달 |
| CAN Bus | ✅ 우선순위 기반 하드웨어 보장 |
| ECU / RTOS | ✅ 하드 리얼타임 |

---

## CarWatchdog — Keep Alive 패턴

```
앱 → tellClientAlive() → Watchdog  (heartbeat)
앱 → tellClientAlive() → Watchdog  (heartbeat)
앱 → (무응답 3초)
                          Watchdog → 앱 강제 재시작
```

일반 ANR: 사용자가 판단 → 대기 or 종료  
CarWatchdog: 시스템이 자동 복구 → 강제 재시작

---

## 핵심 인사이트

> Android와 RTOS 사이에서 크리티컬한 실시간성이 필요하다면
> Android 레이어를 최대한 얇게 유지하고
> 실제 보장은 CAN Bus + ECU에 위임하는 것이 올바른 설계.
>
> IVI 플랫폼 엔지니어의 역할:
> 각 레이어가 책임질 수 있는 것과 없는 것을 명확히 알고
> 경계를 올바르게 설계하는 것.

## 관련 개념
- VHAL (Vehicle HAL)
- CAN Bus, LIN Bus, Automotive Ethernet
- CarPropertyManager, CarWatchdogManager
- AUTOSAR, QNX
- ISO 26262 ASIL

---
*2026-06-24*
