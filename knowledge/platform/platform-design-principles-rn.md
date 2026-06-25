# 플랫폼 레이어 개발자의 설계 원칙 — React Native

> 네이티브가 공짜로 주는 것을 RN에서는 개발자가 의식적으로 구현해야 한다

---

## 1. 상태 머신 — RN에서 더 중요

네이티브는 플랫폼이 생명주기를 강제하지만, RN은 암묵적 상태가 더 많이 생긴다.

```typescript
// 평범한 코드 — 불가능한 조합도 허용
const [isListening, setIsListening] = useState(false);
const [isLoading, setIsLoading] = useState(false);
// isListening=true, isLoading=true 동시에? 버그

// 뛰어난 코드
type VoiceState =
  | { type: 'idle' }
  | { type: 'listening' }
  | { type: 'processing'; input: string }
  | { type: 'speaking'; response: string }
  | { type: 'error'; reason: string }
  | { type: 'safety_interrupted' };

function transition(state: VoiceState, event: Event): VoiceState {
  switch (`${state.type}:${event.type}`) {
    case 'idle:WAKE_WORD':       return { type: 'listening' };
    case 'listening:SPEECH_END': return { type: 'processing', input: event.input };
    case 'processing:SAFETY':    return { type: 'safety_interrupted' };
    default:                     return { type: 'error', reason: 'invalid_transition' };
  }
}
```

**Kotlin과의 차이:**
- Kotlin: `sealed class` + `when` → 컴파일러가 누락 분기를 강제
- RN: TypeScript union + switch → 런타임에서 `default`로 잡아야 함
- 복잡해지면 XState 도입 고려 (상태 전이를 선언적으로 관리)

---

## 2. 관찰 가능성 — JS Thread 병목 측정

```typescript
class PipelineTrace {
  private steps: Record<string, number> = {};

  async measure<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    const result = await fn();
    this.steps[name] = Math.round(performance.now() - start);
    return result;
  }

  report() {
    const entries = Object.entries(this.steps)
      .map(([k, v]) => `[${k}: ${v}ms]`).join(' ');
    const total = Object.values(this.steps).reduce((a, b) => a + b, 0);
    console.log(`Pipeline: ${entries} total: ${total}ms`);
    // 출력: Pipeline: [stt: 312ms] [llm: 1843ms] [nav: 67ms] total: 2222ms
  }
}

// JS Thread 블로킹 방지
InteractionManager.runAfterInteractions(() => {
  processHeavyTask(); // 애니메이션 끝난 후 실행
});
```

**Kotlin과의 차이:**
- Kotlin: GC, 스레드 경합이 병목
- RN: **JS Thread 자체가 싱글 스레드** → 연산이 길면 UI 프레임 드롭
- `InteractionManager`로 애니메이션 완료 후 무거운 작업 실행
- Flipper / React Native Debugger로 JS Thread FPS 측정

---

## 3. 백프레셔 — AbortController / RxJS

Kotlin의 `Channel(DROP_OLDEST)`, `conflate()` 같은 언어 레벨 지원이 없어 직접 구현해야 한다.

```typescript
// RxJS switchMap — 이전 요청 자동 취소
voiceSubject.pipe(
  debounceTime(300),
  switchMap(input => from(processVoice(input)))
).subscribe(handleResult);

// 또는 AbortController 직접 구현
let currentController: AbortController | null = null;

async function handleVoiceInput(input: string) {
  currentController?.abort();
  currentController = new AbortController();

  try {
    const result = await llmClient.query(input, {
      signal: currentController.signal
    });
    handleResult(result);
  } catch (e) {
    if (e.name === 'AbortError') return; // 취소된 것은 무시
    handleError(e);
  }
}
```

**선택 기준:**
| 상황 | 선택 |
|---|---|
| 이미 RxJS 사용 중 | `switchMap` |
| fetch/axios 기반 | `AbortController` |
| 상태 관리와 통합 필요 | XState의 invoke + cancel |

---

## 4. 타임아웃 + 재시도 + 폴백

```typescript
async function fetchWithGuard<T>(
  fn: () => Promise<T>,
  options: { timeout: number; retries: number; fallback: () => T }
): Promise<T> {
  for (let attempt = 0; attempt <= options.retries; attempt++) {
    try {
      return await Promise.race([
        fn(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('timeout')), options.timeout)
        )
      ]);
    } catch (e) {
      if (attempt === options.retries) return options.fallback();
      await delay(500 * (attempt + 1)); // 지수 백오프
    }
  }
  return options.fallback();
}

// 네트워크 상태 감지 추가 — 네이티브에 없는 RN 고유 고려사항
const netState = await NetInfo.fetch();
if (!netState.isConnected) return offlineFallback();
```

**Kotlin과의 차이:**
- Kotlin: `withTimeout {}` 코루틴 내장 → 취소가 구조적으로 전파됨
- RN: `Promise.race()`로 직접 구현 → `AbortController`와 함께 써야 실제 요청도 취소됨
- 타임아웃만 걸면 JS Promise는 resolve/reject를 기다리는 상태가 됨 (메모리 누수 가능)

---

## 5. 레이어 경계 명시화

네이티브는 플랫폼이 레이어 경계를 강제하지만, RN은 개발자가 의식적으로 분리해야 한다.

```typescript
// infrastructure/native/SttClient.ts  ← Native 레이어
class SttClient {
  async transcribe(audio: string): Promise<string> {
    return NativeModules.STT.transcribe(audio);
  }
}

// infrastructure/api/LlmClient.ts     ← Network 레이어
class LlmClient {
  async query(input: string, signal?: AbortSignal): Promise<string> {
    const res = await fetch('/api/llm', { body: input, signal });
    return res.text();
  }
}

// domain/VoicePipeline.ts             ← 비즈니스 로직
class VoicePipeline {
  constructor(
    private stt: SttClient,
    private llm: LlmClient,
    private tts: TtsClient,
  ) {}

  async process(audio: string): Promise<void> {
    const input  = await this.stt.transcribe(audio);
    const result = await this.llm.query(input);
    await this.tts.speak(result);
  }
}
```

**왜 중요한가:**
- `NativeModules` 직접 호출이 비즈니스 로직에 섞이면 테스트 불가
- 레이어를 분리하면 Native → Mock 교체만으로 JS 레이어 단독 테스트 가능
- Kotlin 대비 RN은 파일 구조로만 경계를 표현하므로 팀 컨벤션이 더 중요

---

## 네이티브 vs RN 비교

| 원칙 | Kotlin | React Native |
|---|---|---|
| 상태 머신 | `sealed class` + `when` (컴파일 체크) | TypeScript union + XState (런타임) |
| 관찰 가능성 | PipelineTrace + logcat | PipelineTrace + JS Thread FPS 측정 |
| 백프레셔 | `Channel` + `conflate()` (언어 내장) | RxJS `switchMap` / `AbortController` (직접 구현) |
| 타임아웃/재시도 | `withTimeout` + `retry` (구조적 취소) | `Promise.race` + 직접 구현 (누수 주의) |
| 레이어 경계 | 플랫폼이 강제 | 개발자가 명시적 설계 |
| 병목 위치 | GC, 스레드 경합 | JS Thread 블로킹 |

---

## 핵심 인사이트

> RN에서 뛰어난 코드는
> "네이티브가 공짜로 주는 것"을
> JS 레이어에서 의식적으로 구현한 코드다.

---

## 관련 개념

- XState (상태 머신 라이브러리)
- RxJS `switchMap`, `debounceTime`
- `AbortController`, `AbortSignal`
- `InteractionManager`, `requestAnimationFrame`
- `NetInfo`, 오프라인 폴백
- Flipper, React Native Debugger (JS Thread FPS 측정)

## 관련 문서

- [[platform-design-principles-kotlin]] — Kotlin 버전
- [[react-native-lifecycle-limits]] — RN 생명주기 한계
- [[react-native-native-mapping]] — RN-네이티브 개념 매핑

---
*2026-06-25 | React Native / TypeScript*
