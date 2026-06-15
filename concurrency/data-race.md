# Data Race와 동시성 안전 기법

> **Context**: Launcher 프로젝트의 `NsdModuleManager` 코틀린 코드에서 data race 방지 대책을 정리하면서 학습한 내용.

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

| | `@Volatile` | `AtomicBoolean` |
|---|---|---|
| 메모리 가시성 | ✅ | ✅ |
| 단일 읽기/쓰기 원자성 | ✅ | ✅ |
| 복합 연산 원자성 (CAS) | ❌ | ✅ |

---

## 언어별 비교

### Java / Kotlin

- `@Volatile`: 메모리 가시성만 보장
- `AtomicBoolean`, `AtomicInteger` 등: CAS 기반 lock-free 원자 연산

### TypeScript / JavaScript

- **싱글 스레드**이므로 data race 자체가 없음
- `async/await`의 비동기 컨텍스트 전환 문제는 별개 (race condition은 존재)

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
