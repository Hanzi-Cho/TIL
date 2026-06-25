# Binder mmap 동작 원리와 블로킹

> "버퍼를 안 거친다는 게 어떻게 가능한가, 지연되면 어떡하나"

## mmap이 복사를 줄이는 원리

```
소켓:
프로세스 A 메모리
    → send buffer (복사 1)
    → recv buffer (복사 2)
    → 프로세스 B 메모리

Binder:
프로세스 A 메모리
    → 커널 mmap 영역 (복사 1)
    → 프로세스 B가 직접 읽음 (복사 없음)
```

mmap 영역이 **프로세스 B의 가상 주소 공간에 이미 매핑**되어 있어서  
별도 recv buffer로 복사할 필요가 없다.

```
프로세스 B 가상 주소 공간:
┌──────────────────────────────┐
│  B의 코드/데이터              │
│  커널 mmap 영역 ◀────────────│ ← 이미 여기에 매핑됨
│  (Binder 버퍼)               │   복사 없이 직접 참조
└──────────────────────────────┘
```

mmap도 버퍼이긴 하지만, **별도 복사 없이 B가 직접 참조 가능한 버퍼**다.

---

## 지연 문제 — Binder는 기본적으로 동기(synchronous)

```
프로세스 A
    │
    │ binder 호출 → 블로킹
    │               프로세스 B 응답까지 대기
    ▼ 응답 받으면 재개
```

B가 느리면 A가 그냥 기다린다.  
**메인 스레드에서 Binder 호출 → ANR 위험** (Looper 블로킹과 동일한 문제)

---

## 대응 방법

### ① oneway — 응답 불필요한 호출

```java
// AIDL
interface IMyService {
    oneway void doSomething(); // 즉시 리턴, 응답 안 기다림
}
```

### ② 백그라운드 스레드에서 호출

```kotlin
viewModelScope.launch(Dispatchers.IO) {
    val result = someService.heavyOperation() // IO 스레드에서 블로킹
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

### ③ StrictMode로 메인 스레드 Binder 호출 감지

```kotlin
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectCustomSlowCalls()
        .penaltyLog()
        .build()
)
```

---

## 핵심 인사이트

> mmap은 "복사 횟수를 줄이는" 최적화지, 지연 자체를 없애는 게 아니다.
> Binder 호출이 느린 서비스를 만나면 그대로 블로킹된다.
> Binder 호출은 항상 백그라운드 스레드에서 하는 게 원칙.

## 관련 개념
- oneway AIDL, BC_TRANSACTION / BR_REPLY
- ANR, Looper 블로킹
- StrictMode
- mmap, 가상 주소 공간

---
*2026-06-24*
