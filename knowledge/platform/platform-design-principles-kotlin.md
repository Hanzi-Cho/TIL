# 플랫폼 레이어 개발자의 설계 원칙 — Kotlin

> 코드보다 판단이 본질 — 코드는 그 판단의 결과물

뛰어난 플랫폼 레이어 개발자는 **정상 동작보다 실패 시나리오를 더 정교하게** 다룬다.
"이게 실패하면 어떡하지"를 설계 단계에서 강제하는 구조가 좋은 코드의 본질.

---

## 1. 상태 머신 (State Machine) 명시화

상태를 암묵적 bool 조합으로 표현하면 조합 폭발이 생긴다.

```kotlin
// 평범한 코드 — 상태가 암묵적, 조합 폭발
var isListening = false
var isProcessing = false
var isSpeaking = false
// isListening=true && isProcessing=true 가 가능한가? 불분명

// 뛰어난 코드 — 상태를 명시적으로 정의
sealed class VoiceState {
    object Idle : VoiceState()
    object Listening : VoiceState()
    data class Processing(val input: String) : VoiceState()
    data class Speaking(val response: String) : VoiceState()
    data class Error(val reason: ErrorReason) : VoiceState()
    object SafetyInterrupted : VoiceState()
}

// 허용된 전이만 가능 — 나머지는 컴파일 타임 또는 명시적 에러
fun transition(current: VoiceState, event: Event): VoiceState {
    return when (current to event) {
        Idle to Event.WakeWord         -> Listening
        Listening to Event.SpeechEnd   -> Processing(event.input)
        Processing to Event.SafetyAlert -> SafetyInterrupted
        else -> Error(ErrorReason.InvalidTransition)
    }
}
```

**왜 중요한가:**
- 상태 머신 없으면 "처리 중 안전 알림 오면 어떡하지"가 코드 곳곳에 흩어짐
- sealed class로 가능한 상태를 닫아두면 when 분기에서 컴파일러가 누락을 잡아줌
- IVI/차량 도메인에서 안전 인터럽트는 어느 상태에서도 전이 가능해야 함 → `SafetyInterrupted` 명시

---

## 2. 관찰 가능성 (Observability) — 측정 근거 확보

숫자에는 출처가 있어야 한다. "LLM 3초 타임아웃"이 어디서 나왔는지 설명할 수 없으면 튜닝도 디버깅도 불가능.

```kotlin
// 평범한 코드 — 블랙박스
val result = llmClient.query(input)

// 뛰어난 코드 — 각 스텝 측정
suspend fun processWithTrace(input: String): Result {
    val trace = PipelineTrace()

    val sttResult = trace.measure("stt") {
        sttClient.transcribe(input)      // 실측: 200~500ms
    }
    val llmResult = trace.measure("llm") {
        llmClient.query(sttResult)       // 실측: 1~3s
    }
    val navResult = trace.measure("nav") {
        navApi.setDestination(llmResult) // 실측: 50~100ms
    }

    trace.report()
    // 출력: [stt: 312ms] [llm: 1843ms] [nav: 67ms] total: 2222ms
    return navResult
}
```

**왜 중요한가:**
- 타임아웃 값이 측정 기반이 아니면 너무 짧아 정상 요청을 죽이거나, 너무 길어 사용자 경험을 망침
- 프로덕션에서 지연 증가를 감지하려면 각 스텝별 측정값이 있어야 함
- OpenTelemetry / 자체 trace 구조로 확장 가능

---

## 3. 동시성 컨트롤 + 백프레셔 (Backpressure)

무한정 쌓이는 큐는 OOM과 오래된 명령 실행이라는 두 가지 위험을 만든다.

```kotlin
// 평범한 코드 — 무한정 쌓임, OOM 위험
val requestQueue = LinkedBlockingQueue<VoiceRequest>()

// 뛰어난 코드 — 백프레셔 적용
val requestChannel = Channel<VoiceRequest>(
    capacity = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST // 오래된 것 버림
)

// Flow로 처리
voiceInputFlow
    .conflate()  // 처리 못 따라가면 최신 것만 유지
    .collect { processVoiceInput(it) }
```

**왜 중요한가:**
- IVI에서 사용자가 빠르게 여러 번 말해도 가장 최근 명령만 처리하는 게 UX상 올바름
- `DROP_OLDEST`는 IVI 음성 명령에, `DROP_LATEST`는 실시간 센서 처리에 적합
- `conflate()`는 중간 값을 버리고 최신 값만 소비 → 과부하 방어

---

## 4. 타임아웃 + 재시도 + 폴백

외부 시스템(LLM, 네트워크 API)은 반드시 실패한다. 설계 단계에서 명시적으로 처리해야 한다.

```kotlin
suspend fun queryLlm(input: String): String {
    return withTimeout(3_000) {          // 측정 기반 타임아웃 (실측 p99 기준)
        retry(times = 2, delay = 500) {  // 재시도 (일시적 장애 대응)
            llmClient.query(input)
        }
    } ?: fallback()                      // 폴백: "다시 말씀해주세요"
}
```

**설계 기준:**
| 구성 요소 | 설정 기준 |
|---|---|
| 타임아웃 | 실측 p99 × 1.5 (측정 없이 설정 금지) |
| 재시도 횟수 | 2~3회 (그 이상은 레이턴시 합산으로 역효과) |
| 재시도 딜레이 | 지수 백오프 권장 (500ms → 1000ms → ...) |
| 폴백 | 사용자에게 명확한 피드백, 상태 머신에서 Error 상태로 전이 |

---

## 5. 시퀀스 다이어그램으로 팀 소통

구현 전에 경계 합의가 먼저다. 각 스텝의 책임자, 지연, 실패 시나리오를 다이어그램으로 명시.

```
[User Voice]
     │
     ▼
[STT Service] ──실패──→ [Error: STT Failed]
     │ (200~500ms)
     ▼
[LLM API] ──타임아웃──→ [Fallback: "다시 말씀해주세요"]
     │ (1~3s)
     ▼
[Navigation API] ──실패──→ [Error: Nav Unavailable]
     │ (50~100ms)
     ▼
[SafetyMonitor] ──언제든 인터럽트 가능──→ [SafetyInterrupted]
```

**왜 중요한가:**
- 팀원(앱 개발자, 플랫폼 팀, QA)이 코드를 보기 전에 흐름을 이해할 수 있음
- 실패 경로가 다이어그램에 없으면 구현에서도 없을 가능성 높음
- 경계 합의가 나중에 "그건 내 책임 아님" 논쟁을 막는다

---

## 전체 설계 순서

```
1. 상태 머신으로 가능한 상태/전이 명시적 정의
        ↓
2. 각 스텝 지연 측정 → 타임아웃 근거 확보 (Observability)
        ↓
3. 동시성 컨트롤 + 백프레셔로 과부하 방어
        ↓
4. 타임아웃, 재시도, 폴백 시나리오 설계
        ↓
5. 시퀀스 다이어그램으로 팀과 소통
```

---

## 핵심 인사이트

> 뛰어난 플랫폼 레이어 개발자는
> 정상 동작보다 **실패 시나리오를 더 정교하게** 다룬다.
>
> "이게 실패하면 어떡하지"를 설계 단계에서 강제하는 구조가
> 좋은 코드의 본질이다.

---

## 관련 개념

- State Machine, `sealed class`, `when` exhaustive check
- Backpressure, `Channel`, `conflate()`, `BufferOverflow`
- Observability, Tracing, OpenTelemetry
- `withTimeout`, `retry`, fallback
- Defensive Programming
- 시퀀스 다이어그램 (PlantUML, Mermaid)

## 관련 문서

- [[platform-design-principles-rn]] — React Native 버전
- [[android-latency-minimization]] — Android 레이턴시 최소화 기법
- [[looper-handler-messagequeue]] — Android 동시성 기초

---
*2026-06-25 | Kotlin*
