# Data Race와 동시성 안전 기법

> **Context**: Launcher 프로젝트의 `NsdManagerModule.kt`에서 실제로 발견된 data race 버그를 분석하면서 학습한 내용.
> NSD 콜백 스레드와 메인 스레드가 `isResolving`, `activeResolveSessionId` 등 공유 필드에 `@Volatile` 없이 동시 접근해 이중 resolve, 무효 세션 이벤트 방출이 발생할 수 있었다.
> 같은 로직을 TypeScript(React Native JS 레이어)로 작성했다면 이 버그 자체가 존재하지 않는다는 점이 두 환경의 결정적 차이다.

---

## Data Race란?

두 개 이상의 스레드가 **공유 변수에 동시에 접근**하면서 그 중 하나 이상이 쓰기를 수행할 때 발생.
결과가 실행 순서(스케줄링)에 따라 달라지므로 재현하기 어렵고 디버깅이 까다롭다.

### Check-Then-Act 패턴의 위험

```kotlin
if (!initialized) {   // (1) 읽기
    initialized = true // (2) 쓰기
    init()            // (3) 초기화
}
```

스레드 A가 (1)을 실행한 직후, 스레드 B도 (1)을 실행하면 둘 다 `init()`을 호출하게 된다.

---

## 해결 기법

### 1. `@Volatile` — 메모리 가시성 보장

```kotlin
@Volatile
private var initialized: Boolean = false
```

- 변수를 **CPU 캐시가 아닌 메인 메모리에서 직접 읽고 쓴다** → 메모리 가시성(Memory Visibility) 보장
- **보장하지 않는 것**: 복합 연산의 원자성
  - 읽기 → 판단 → 쓰기 사이에 다른 스레드가 끼어들 수 있음
  - Check-Then-Act 문제를 완전히 해결하지 못함
- 사용처: 단순 플래그 읽기처럼 **단일 읽기/쓰기만 필요한 경우**

---

### 2. `AtomicBoolean` — 복합 연산의 원자성 보장

```kotlin
private val initialized = AtomicBoolean(false)

// CAS(Compare-And-Swap): expected=false일 때만 true로 변경하고 성공 여부 반환
if (initialized.compareAndSet(false, true)) {
    init()
}
```

- **CAS (Compare-And-Swap)**: 비교와 교환을 **단일 CPU 명령어**로 수행
  - `compareAndSet(expected, update)`: 현재 값 == expected 이면 update로 바꾸고 `true` 반환
- Lock 없이 원자성을 보장하는 **lock-free** 방식
- `@Volatile`의 가시성 보장 + 복합 연산의 원자성 보장을 모두 충족
- Check-Then-Act 문제를 완전히 해결

#### 내부 구현: 왜 `volatile int`로 bool을 저장하는가?

Java의 `AtomicBoolean`은 내부적으로 `volatile int value`로 boolean 값을 저장한다.

```java
// AtomicBoolean 내부 (OpenJDK)
private volatile int value; // 0 = false, 1 = true
```

이유는 두 가지가 맞물려 있다.

**① CPU의 최소 처리 단위(Word) 때문에 int 사용**

CPU는 1비트짜리 boolean을 단독으로 읽고 쓰는 명령어가 없다. 대부분의 아키텍처에서 최소 처리 단위는 **32비트(4바이트)** 이며, 이 단위에 맞춰 정렬된 데이터는 **단일 명령어로 읽고 쓸 수 있어 tearing(찢어짐)이 없다.** `int`가 이 조건을 만족하므로 bool 대신 int를 사용한다.

> 참고: WORD 크기는 아키텍처마다 다르다 (x86: 32비트, x86-64: 64비트). "4비트"는 니블(nibble)로 전혀 다른 개념이다.

**② volatile로 Memory Fence(메모리 장벽) 적용**

`volatile`이 붙으면 읽기/쓰기 시점에 **Memory Fence 명령**이 삽입된다.

- **쓰기 시**: 현재 코어의 캐시 변경 내용을 메인 메모리에 flush
- **읽기 시**: 자신의 캐시를 invalidate하고 메인 메모리에서 새로 읽음
- 다른 코어는 MESI 같은 **캐시 일관성 프로토콜**을 통해 해당 캐시 라인이 갱신됐음을 인지하고 스스로 캐시를 무효화함

즉, "다른 스레드의 캐시를 직접 무효화"하는 게 아니라, Fence + 캐시 일관성 프로토콜이 협력하여 모든 코어가 같은 값을 보도록 보장하는 구조다.

**세 가지의 합산 결과**

```
non-tearing (int 정렬)  → 명령이 찢어지지 않음
Memory Fence (volatile) → 가시성 보장
CAS 명령어              → 복합 연산의 원자성
= AtomicBoolean의 완전한 스레드 안전성
```

| | `@Volatile` | `AtomicBoolean` | `synchronized` |
|---|---|---|---|
| 메모리 가시성 | ✅ | ✅ | ✅ |
| 단일 읽기/쓰기 원자성 | int 이하만 ✅ | ✅ | ✅ |
| 복합 연산 원자성 (CAS) | ❌ | ✅ | ✅ |
| 임계 구역 전체 보호 | ❌ | ❌ | ✅ |

#### 보충: `long` / `double`의 Word Tearing

JVM 스펙(JLS §17.7)은 `long`(64비트)과 `double`(64비트)의 읽기/쓰기를 **원자적으로 보장하지 않는다.**
32비트 JVM에서는 상위 32비트, 하위 32비트를 **두 번에 나눠 쓸 수 있어** tearing이 발생할 수 있다.

```kotlin
// 스레드 A: Long.MAX_VALUE(0x7FFF_FFFF_FFFF_FFFF)를 쓰는 중
// 스레드 B: 읽으면 상위/하위가 섞인 쓰레기 값(예: 0x7FFF_FFFF_0000_0000)을 읽을 수 있음
var sharedLong: Long = 0L  // @Volatile 없으면 위험
```

해결책: `@Volatile`을 붙이면 64비트 접근도 원자적으로 처리하도록 JVM이 보장한다.
`boolean`, `int`, 참조형(reference)은 32비트 이하이므로 `@Volatile` 없이도 tearing은 없다
(단, 가시성 문제는 여전히 존재).

---

### 3. `synchronized` — 임계 구역 전체를 상호 배제

CAS는 **단일 변수 하나**에 최적화된 방식이다. 여러 변수를 함께 갱신하거나 복잡한 로직 전체를 보호해야 할 때는 `synchronized`를 쓴다.

```kotlin
// 메서드 전체를 잠금
@Synchronized
fun processNext() {
    if (!isResolving) {
        isResolving = true  // 여러 변수를
        activeSessionId++   // 동시에 일관되게 갱신
        resolve()
    }
}

// 특정 블록만 잠금 (lock 객체를 명시)
private val lock = Any()

fun enqueue(item: ServiceInfo) {
    synchronized(lock) {
        resolveQueue.add(item)
        if (!isResolving) processNext()
    }
}
```

- 진입 시 **monitor lock** 획득, 탈출 시 자동 해제 → 데드락 위험은 있으나 누락 위험은 없음
- `@Volatile` + 원자성 + 상호 배제를 모두 커버
- `AtomicBoolean`보다 무겁지만, 보호해야 할 상태가 여러 개일 때 훨씬 안전

> **실제 버그 연결**: `NsdManagerModule.kt`의 `processNextResolve()`는 `isResolving`, `isDiscovering`, `activeResolveSessionId`를 한 블록에서 함께 변경한다.
> 이 세 변수를 원자적으로 묶으려면 CAS 세 개로는 부족하고, 하나의 `synchronized(lock)` 블록이 정확한 해법이다.

---

### 4. CAS의 한계 — ABA 문제

CAS는 "현재 값 == expected"이면 교체한다. 그런데 값이 **A → B → A**로 변했다면?

```
스레드 A: 값 = A 확인 (compareAndSet 직전에 정지)
스레드 B: A → B → A 로 값을 두 번 바꿈
스레드 A: 재개 — 값이 여전히 A이므로 CAS 성공
          그러나 B를 거쳤다는 사실은 놓침
```

`AtomicBoolean`은 `false → true → false` 사이클이 가능하지만 boolean 특성상 실무 문제가 되는 경우가 드물다.
문제는 **lock-free 스택이나 큐** 같은 자료구조에서 발생한다: 노드가 제거됐다가 같은 주소로 재할당되면 CAS가 "변경 없음"으로 잘못 판단해 **이미 제거된 노드를 살아있는 것으로 취급**하는 버그가 생긴다.

#### 해결: `AtomicStampedReference` (버전 번호 추가)

```kotlin
// AtomicBoolean 대신 stamp(버전)를 함께 관리
val ref = AtomicStampedReference<String>("A", 0)

val stamp = intArrayOf(0)
val current = ref.get(stamp)          // 현재 값 + 버전 동시 조회
ref.compareAndSet(
    current, "B",                     // 값 교체
    stamp[0], stamp[0] + 1            // 버전도 함께 증가
)
// 이제 A → B → A 시도 시 버전이 달라 CAS 실패 → ABA 방지
```

| | CAS (`AtomicBoolean`) | `AtomicStampedReference` |
|---|---|---|
| 단일 변수 원자성 | ✅ | ✅ |
| ABA 문제 | ❌ (발생 가능) | ✅ (버전으로 방지) |
| 복잡도 | 단순 | 높음 |
| 사용 시기 | boolean/int 단순 플래그 | lock-free 자료구조, 포인터 기반 연산 |

---

## 언어별 비교

### Java / Kotlin

- `@Volatile`: 가시성 보장 + `long`/`double` tearing 방지
- `AtomicBoolean` / `AtomicInteger` 등: CAS 기반 lock-free 원자 연산
- `synchronized`: 임계 구역 전체 상호 배제
- `java.util.concurrent.locks.ReentrantLock`: `synchronized`보다 세밀한 제어 (tryLock, timeout 등)

### TypeScript / JavaScript — "Data Race가 구조적으로 불가능한 환경"

**싱글 스레드 이벤트 루프** 모델이라 data race 자체가 언어 설계 수준에서 존재하지 않는다.
Kotlin에서 발생한 `NsdManagerModule.kt` 버그가 TypeScript였다면 어떻게 달랐는지 구체적으로 비교한다.

#### 실제 버그: Kotlin `NsdManagerModule.kt`

NSD(네트워크 서비스 탐색) 모듈에서 두 스레드가 공유 변수에 동시 접근했다.

```kotlin
// NSD 콜백 스레드에서 호출됨
override fun onServiceFound(serviceInfo: NsdServiceInfo) {
    synchronized(resolveQueue) {
        resolveQueue.add(serviceInfo)
    }
    processNextResolve()  // ← NSD 스레드에서 직접 실행
}

// 메인 스레드의 타임아웃 핸들러에서도 호출됨
mainHandler.postDelayed({
    processNextResolve()  // ← 메인 스레드에서 실행
}, resolveTimeoutMs)

// processNextResolve 내부: @Volatile 없이 공유 필드 접근
private fun processNextResolve(...) {
    if (!isDiscovering) return           // 두 스레드가 동시에 읽음
    if (isResolving && retryCount == 0) return
    isResolving = true                   // 두 스레드가 동시에 씀
    val id = activeResolveSessionId + 1  // 비원자적 read-modify-write
    activeResolveSessionId = id
}
```

**결과**: 두 스레드가 모두 `isResolving = false`를 읽고 진입 → `resolveService()` 이중 호출 → 같은 서비스가 두 번 발견된 것처럼 이벤트 방출 또는 세션 ID 불일치로 무효 결과 수신.

#### 같은 로직을 TypeScript로 작성하면

```typescript
// useMdnsDiscovery.ts — React Native JS 레이어
// NSD 이벤트는 네이티브 → JS 브리지를 거쳐 메인 JS 스레드로 직렬화됨

let isResolving = false;          // 단순 변수로 충분
let activeSessionId = 0;

function processNextResolve() {
    if (!isDiscovering) return;
    if (isResolving) return;      // 이 검사가 항상 안전
                                  // JS는 싱글 스레드이므로 두 실행 흐름이
                                  // 이 줄을 '동시에' 실행하는 것이 불가능
    isResolving = true;
    activeSessionId += 1;         // read-modify-write도 원자적
    resolve();
}

// 이벤트 A와 타임아웃 B가 '동시에' 오더라도
// 이벤트 루프는 A를 완전히 처리한 뒤 B를 처리한다
// processNextResolve()는 항상 한 번에 하나씩 실행된다
```

**차이의 근거: 이벤트 루프(Event Loop) 모델**

```
Kotlin (JVM, 멀티스레드)         TypeScript (V8, 싱글스레드)
┌─────────────────────┐          ┌─────────────────────────┐
│ NSD 콜백 스레드     │          │ Call Stack (하나뿐)      │
│  └─ processNext()   │◀─ race   │  └─ processNext()        │
│ 메인 스레드         │          │                          │
│  └─ processNext()   │          │ Event Queue              │
└─────────────────────┘          │  ├─ nsd 이벤트           │
  두 스레드가 동시에 실행          │  └─ timeout 콜백         │
  → data race 발생               │                          │
                                 │ 콜 스택이 비어야만        │
                                 │ 큐에서 꺼내 실행          │
                                 │ → 동시 실행 자체가 없음   │
                                 └─────────────────────────┘
```

- JS 엔진(V8)은 **콜 스택이 하나**다. 함수 A가 실행 중이면 함수 B는 무조건 대기한다.
- 네이티브 레이어(Kotlin)에서 온 이벤트는 **JS 브리지를 통해 이벤트 큐에 삽입**되고, 현재 실행 중인 JS 작업이 끝난 뒤 순서대로 처리된다.
- 따라서 `isResolving`, `activeSessionId`는 `@Volatile`도, `AtomicBoolean`도, `synchronized`도 필요 없다.

#### TypeScript에도 있는 것: Race Condition (data race와 다름)

data race(동시 접근)는 없지만, **비동기 작업 사이의 논리적 경쟁**은 존재한다.

```typescript
// 이 두 줄 사이에 await가 있으면 다른 이벤트가 끼어들 수 있음
const val = await db.get('count');   // (1) 읽기 — 여기서 다른 코루틴이 실행될 수 있음
await db.set('count', val + 1);      // (2) 쓰기 — (1)이 읽은 값이 이미 낡은 값일 수 있음

// 동시 호출 시나리오:
// A: val = 5 읽음, 일시 정지
// B: val = 5 읽음, 6으로 씀 (count = 6)
// A: 재개, 5+1=6으로 씀 (B의 결과 덮어씀) → count가 7이 아닌 6
```

| | Kotlin (JVM) | TypeScript (JS) |
|---|---|---|
| Data Race (동시 접근) | ✅ 발생 가능 | ❌ 구조적으로 불가 |
| Race Condition (논리적 경쟁) | ✅ 발생 가능 | ✅ 발생 가능 (`await` 사이) |
| 보호 수단 | `@Volatile`, `Atomic*`, `synchronized` | 로직으로 방어 (플래그, 취소 토큰 등) |
| NsdManagerModule 버그 재현 여부 | ✅ 실제 발생 | ❌ 불가 |

### C / C++

- `volatile`: **컴파일러 최적화 방지** 용도 (메모리 매핑 IO, 하드웨어 레지스터 접근 등)
  - CPU 레벨의 메모리 재정렬(instruction reordering)은 막지 못해 멀티스레드에서 의미 없음
  - Java/Kotlin의 `@Volatile`과 **완전히 다른 개념**
- 멀티스레드 안전성은 **Mutex** 사용
  - Mutex의 실제 한계: **데드락(deadlock)** 위험, lock/unlock **성능 오버헤드**
  - 공유 자원 접근 구간이 직렬화되는 건 한계가 아니라 정상 동작

```cpp
std::mutex mtx;
std::lock_guard<std::mutex> lock(mtx); // RAII 방식 자동 해제
initialized = true;
```

### Rust

- **컴파일 단계에서 data race를 원천 차단** (소유권 시스템)
- `std::sync::atomic::Ordering`으로 메모리 순서를 개발자가 명시적으로 지정

| Ordering | 의미 | 성능 |
|---|---|---|
| `Relaxed` | 원자성만 보장, 재정렬 허용 | 가장 빠름 |
| `Acquire` | 이후 읽기가 앞으로 올라오지 않음 | 중간 |
| `Release` | 이전 쓰기가 뒤로 내려가지 않음 | 중간 |
| `AcqRel` | Acquire + Release 동시 적용 | 중간 |
| `SeqCst` | 모든 스레드에서 전역 순서 보장 | 가장 느림 |

```rust
use std::sync::atomic::{AtomicBool, Ordering};
let initialized = AtomicBool::new(false);
initialized.compare_exchange(false, true, Ordering::SeqCst, Ordering::Relaxed);
```

### Go

Go의 철학: **"메모리를 공유해서 통신하지 말고, 통신으로 메모리를 공유하라"**
> *Don't communicate by sharing memory; share memory by communicating.*

- **채널(Channel)**: 데이터를 직접 공유하지 않고 채널을 통해 전달
  - 하나의 고루틴만 데이터를 소유하게 하여 race 방지
- `sync.Mutex`도 사용 가능하나, 채널 방식을 권장
- `go run -race` 플래그로 race condition 런타임 감지 가능

```go
ch := make(chan bool, 1)

go func() {
    ch <- true // 고루틴이 채널에 값을 보냄
}()

result := <-ch // 메인 고루틴이 채널에서 수신
```

---

## 핵심 정리

```
가시성(Visibility) 문제  → @Volatile
원자성(Atomicity) 문제   → AtomicBoolean (CAS)
상호 배제(Mutual Exclusion) → Mutex / synchronized
소유권 기반 컴파일 타임 보장 → Rust
통신 기반 공유 → Go Channel
```

---

*2026-06-15*
