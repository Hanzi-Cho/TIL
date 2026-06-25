# Android Looper / Handler / MessageQueue

> 메인 스레드가 이벤트 루프 구조인 이유, ANR의 내부 원리

## 구조 한눈에 보기

```
┌─────────────────────────────────────┐
│           Main Thread               │
│                                     │
│  Handler  ──push──▶  MessageQueue   │
│                           │         │
│                        Looper       │
│                        (loop)       │
│                           │         │
│  Handler  ◀─dispatch──────┘         │
└─────────────────────────────────────┘
```

---

## 각 컴포넌트 역할

### MessageQueue — 메시지 저장소

```
[터치 이벤트] → [렌더링] → [onResume] → [DB완료 콜백] → ...
```

줄 세워두는 큐. 스스로 아무것도 하지 않음.

### Looper — 무한 루프로 큐를 소비하는 펌프

```kotlin
while (true) {
    val message = queue.next() // 없으면 대기
    message.target.dispatchMessage(message) // Handler에게 전달
}
```

- 메인 스레드가 살아있는 한 루프가 계속 돌아감
- 스레드를 살아있게 유지하는 것도 Looper의 역할

### Handler — 메시지를 넣고 받는 창구

```kotlin
val handler = Handler(Looper.getMainLooper())

// 다른 스레드에서 메인 스레드로 작업 전달
handler.post {
    textView.text = "업데이트"  // MessageQueue에 삽입됨
}
```

- 생성 시점의 Looper에 묶임
- 메인 핸들러 → 메인 Looper / 백그라운드 핸들러 → 백그라운드 Looper

---

## 전체 흐름

```
IO 스레드: DB 쿼리 완료
    ↓
handler.post { updateUI() }   ← MessageQueue에 삽입
    ↓
Looper가 꺼냄
    ↓
Handler.dispatchMessage()
    ↓
메인 스레드에서 updateUI() 실행
```

> Kotlin 코루틴의 `withContext(Dispatchers.Main)`도 내부적으로 이 Handler를 사용

---

## ANR과의 연결

메인 스레드는 **직렬(serial) 처리** 구조이므로 하나가 블로킹되면 전체가 멈춤.

```
MessageQueue:
├── "터치 이벤트" → DB 쿼리 (3초 블로킹) ← 여기서 멈춤
├── "UI 렌더링"   ← 대기
└── "터치 이벤트" ← 대기
```

**ANR 발생 타임아웃 기준**

| 컴포넌트 | 타임아웃 |
|---|---|
| Activity (입력 이벤트) | 5초 |
| Service | 20초 (Foreground 5초) |
| BroadcastReceiver | 10초 |

> ANR = MessageQueue가 블로킹된 상태를 시스템이 타임아웃으로 감지한 것

---

## Kotlin Dispatcher 매핑

```kotlin
viewModelScope.launch {
    withContext(Dispatchers.IO) {
        db.query() // IO 스레드풀 → MessageQueue 블로킹 없음
    }
    updateUI() // 다시 Main으로 복귀
}
```

| Dispatcher | 내부 구조 | 용도 |
|---|---|---|
| `Dispatchers.Main` | Looper/MessageQueue | UI 작업 |
| `Dispatchers.IO` | 64개 스레드풀 | 네트워크, DB |
| `Dispatchers.Default` | CPU 코어 수 스레드풀 | 연산, 정렬 |

---

## 한 줄 요약

> Handler가 편지를 쓰고, MessageQueue가 우체통, Looper가 집배원

## 관련 개념
- Kotlin Coroutine, CoroutineDispatcher
- ViewRootImpl, Choreographer (렌더링 타이밍)
- StrictMode (메인 스레드 IO 감지 도구)

---
*2026-06-24*
