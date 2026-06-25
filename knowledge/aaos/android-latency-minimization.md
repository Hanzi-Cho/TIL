# Android 실시간성 — 지연 최소화 기법

> Android는 실시간성을 "보장"하는 게 아니라 "최대한 지연을 줄이는" 방향으로 설계

## 기법 목록

### 1. 스레드 우선순위 — Linux 커널 레벨

```kotlin
// JVM 레벨은 약함
Thread.currentThread().priority = Thread.MAX_PRIORITY

// Linux nice값 직접 조작 — 강력
Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO) // nice -19

val vehicleThread = HandlerThread(
    "VehicleThread",
    Process.THREAD_PRIORITY_URGENT_AUDIO
)
```

### 2. 실시간 스케줄러 (SCHED_FIFO) — NDK

```c
// NDK C++
struct sched_param param;
param.sched_priority = 99; // 최고 우선순위
sched_setscheduler(0, SCHED_FIFO, &param);
// 다른 스레드가 절대 선점 불가
// VHAL 내부에서 사용
```

### 3. 메모리 락 (mlockall)

```c
// NDK
mlockall(MCL_CURRENT | MCL_FUTURE);
// 프로세스 메모리를 RAM에 고정
// 페이지 폴트(수백 마이크로초 지연) 제거
```

### 4. Lock-Free 자료구조

```kotlin
// mutex 경합 발생 가능
val queue = LinkedBlockingQueue<VehicleMessage>()

// CAS 기반 Lock-Free 링 버퍼
val ringBuffer = AtomicReferenceArray<VehicleMessage>(1024)
// mutex 없음 → 락 경합 지연 없음
```

### 5. CAN 패킷 전송 경로 최적화

```
일반 경로:
앱 → Binder IPC → VHAL → JNI → NDK → CAN 드라이버 → CAN Bus

최적화 경로:
VHAL (SCHED_FIFO 스레드)
    → 직접 NDK 호출 (Binder 우회)
    → CAN 드라이버
    → CAN Bus
```

Binder IPC 자체가 오버헤드 → 크리티컬 경로에서 Binder 우회.

---

## Android가 보장할 수 없는 이유

```
- 일반 Linux 커널 (non-RT 패치)
- GC 발생 시 수십ms 멈춤
- 커널 인터럽트 지연 보장 불가
```

**해결책:**
- PREEMPT_RT 패치 적용 (일부 차량용 Android)
- GC 압박 최소화 (객체 생성 최소화)
- 결국 크리티컬 경로는 RTOS/ECU로 위임

---

## 할 수 있는 것 vs 없는 것

| | Android |
|---|---|
| 스레드 우선순위 (SCHED_FIFO) | ✅ |
| 메모리 락 (mlockall) | ✅ |
| Lock-Free 자료구조 | ✅ |
| Binder 우회 (NDK 직접) | ✅ |
| GC 완전 제거 | ❌ |
| 커널 인터럽트 응답 보장 | ❌ |
| 마이크로초 단위 결정론적 실행 | ❌ → RTOS 담당 |

---

## 핵심 인사이트

> Android 레이어는 "최대한 빠르게"가 한계.
> "반드시 N마이크로초 안에"는 RTOS만 보장 가능.
>
> IVI 플랫폼 엔지니어는 이 경계를 알고
> Android가 담당할 범위를 최대한 얇게 유지해야 한다.

## 관련 개념
- Linux nice값, SCHED_FIFO, SCHED_RR
- PREEMPT_RT 패치
- CAS (Compare-And-Swap), Lock-Free
- mlockall, 페이지 폴트
- VHAL, CAN Bus

---
*2026-06-24*
