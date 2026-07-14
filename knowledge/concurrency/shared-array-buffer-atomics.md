# SharedArrayBuffer & Atomics (Lock-Free 동기화)

> **대규모 멀티스레드 JS 환경에서 복사 없이 상태를 공유하고, 락프리로 안전하게 동기화하기 위한 명세**

---

## 1. SharedArrayBuffer: 메모리 공유의 3대 모델

JavaScript 스레드(Main Thread와 Web Worker 등) 간에 바이너리 데이터를 넘기는 방식은 크게 3가지 스펙트럼으로 나뉩니다.

### A. 복사 (Structured Clone)
- **방식**: `postMessage(arrayBuffer)`를 사용할 때의 기본 동작.
- **원리**: 데이터를 복제하여 수신 스레드에 새로운 메모리 공간을 할당합니다.
- **단점**: 데이터 크기가 커질수록(예: 10MB 이상) 복사 오버헤드로 인해 심각한 지연 시간(Latency)이 유발됩니다.

### B. 소유권 이전 (Transferable List)
- **방식**: `postMessage(arrayBuffer, [arrayBuffer])` 형식으로 양도 대상 리스트를 명시.
- **원리**: 메모리 복사는 일어나지 않으나, 메모리의 소유권이 송신 스레드에서 수신 스레드로 완전히 **이전(Transfer)**됩니다.
- **제약**: 이전된 후 송신 스레드의 원본 ArrayBuffer는 `detached` 상태가 되어 더 이상 읽거나 쓸 수 없습니다. (공유가 아닌 '이사')

### C. 공유 메모리 (SharedArrayBuffer)
- **방식**: `SharedArrayBuffer` 객체 생성 후 postMessage로 전달.
- **원리**: 복사나 소유권 이전 없이, 여러 스레드가 **동일한 물리 메모리 주소 블록을 동시에 참조(mmap과 유사)**합니다.
- **장점**: 10MB 이상의 대용량 Payload도 전송 비용이 0(Zero-Latency)에 수렴합니다.

---

## 2. Atomics API: 락프리 동기화의 본질

동일한 메모리 블록을 여러 스레드가 동시에 읽고 쓸 때 **데이터 레이스(Data Race)** 및 임계 영역 문제가 발생합니다. 이를 통제하기 위해 `Atomics` API가 필수적입니다.

### A. volatile vs atomic
*   **volatile (가시성 보장)**: CPU 캐싱을 우회하여 항상 실제 메모리 백킹 저장소의 최신 값을 직접 바라보게 강제합니다. (컴파일러의 코드 재배치 방지)
*   **atomic (원자성 보장)**: 특정 메모리 주소에 대해 값을 읽고, 수정하고, 다시 쓰는 연산(Read-Modify-Write, 예: CAS)이 하드웨어(CPU) 레벨에서 도중에 끊기지 않고 단일 사이클처럼 한 번에 수행되도록 보장합니다.

### B. Atomics.wait와 Atomics.notify
단순히 특정 값이 바뀔 때까지 루프를 도는 `while(flag !== 1) {}` (Busy-Wait 폴링)은 CPU 스레드를 계속 점유하여 자원을 100% 낭비시킵니다. 

반면, `Atomics.wait(sharedArray, index, value)`는 조건이 충족될 때까지 스레드를 **OS 수준에서 블로킹(대기 상태)** 시키고 CPU 점유율을 소모하지 않습니다. 이후 다른 스레드에서 연산 완료 후 `Atomics.notify(sharedArray, index, count)`를 호출하면 잠자던 스레드가 즉각 깨어납니다.

> [!WARNING]  
> **Main Thread 블로킹 금지 규칙**: JS 메인 스레드는 UI 이벤트 루프를 처리하므로, 메인 스레드에서 `Atomics.wait()`를 호출하면 즉각 브라우저 크래시나 에러를 유발합니다. 따라서 `Atomics.wait`는 오직 **Web Worker(백그라운드 스레드)** 내에서만 동작하도록 제한해야 합니다.

### C. Promise/콜백과의 차이점
*   Promise나 콜백 동기화는 JS 엔진의 **이벤트 루프 태스크 큐**에 비동기 태스크로 들어가게 됩니다.
*   공유 메모리(SAB) 모델은 메시지 채널을 거치지 않고 메모리 주소를 직접 찔러 작업하므로, 이벤트 루프 스케줄링 오버헤드 없이 스레드 수준에서 즉각 동기 제어가 필요할 때는 `Atomics.wait/notify`를 통한 하부 제어가 훨씬 강건하고 빠릅니다.
