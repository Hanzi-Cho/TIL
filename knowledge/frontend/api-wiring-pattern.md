# 프론트엔드 API 배선 아키텍처 및 실시간 데이터 합성 패턴 (API Wiring & Real-time Integration)

## 1. 4계층 API 호출 아키텍처 (4-Tier API Layering)
프론트엔드 코드의 높은 유지보수성과 단일 진실 공급원(SSOT)을 유지하기 위해, API 통신 레이어를 다음과 같이 4단계로 분리하여 구성한다.

```
[Constants] -> [HttpClient] -> [Services] -> [Custom Hooks] -> [UI Components]
```

1. **상수 계층 (`constants/ApiConstant.ts`)**
   - API 엔드포인트의 베이스 경로 및 라우팅 경로 조각들을 상수로 집중 관리하여 오타를 예방한다.
2. **HTTP 클라이언트 계층 (`api/services/HttpClient.ts`)**
   - Axios 싱글톤 인스턴스를 관리하며, 요청 인터셉터를 통해 JWT 토큰을 자동 첨부하고 응답 인터셉터를 통해 만료된 토큰의 자동 갱신 및 재시도(401/403 대응)를 처리한다.
3. **서비스 인터페이스 계층 (`api/services/*Service.ts`)**
   - 실제 백엔드 API와 통신하는 순수 비동기 함수들(예: `getControllerInfo()`)을 정의하며, 서버 응답 본문에서 실제 데이터 페이로드(`.data.body`)만을 벗겨내어 상위 레이어로 전달한다.
4. **커스텀 훅 계층 (`hooks/*.ts`)**
   - REST API 데이터 패치, 실시간 스트림(SSE/WebSocket) 데이터 합성, 그리고 클라이언트 상태 관리(Zustand)를 결합하여 비즈니스 로직을 추상화한다. UI 컴포넌트는 이 훅만 호출하며 API를 직접 호출하지 않는다.

---

## 2. 실시간 데이터 스트림 합성 및 누적 패턴

대화형 실시간 대시보드 구현 시 성능 최적화를 위해 REST API 폴링(Polling)을 배제하고, **초기 1회 스냅샷 조회(REST) + 실시간 고빈도 이벤트(SSE/WebSocket) 누적** 방식을 활용한다.

### A. Viewer 모니터링 (REST + SSE 단방향 알림 패턴)
- **REST**: 페이지 마운트 시 전체/초기 스냅샷 데이터 조회.
- **SSE (Server-Sent Events)**: 서버로부터 단방향 상태 변경 알림(`groupUpdated`, `blasterUpdated` 등) 수신 시, 알림이 가리키는 특정 엔티티의 ID를 타깃팅하여 부분적인 REST 조회를 재트리거(Refetch)함으로써 네트워크 부하를 줄인다.

### B. Blaster 진행 모니터링 (REST + WebSocket 고빈도 센서 합성 패턴)
- **REST**: 초기 진입 시 대용량 스냅샷을 1회만 패치하여 기본 테이블/도메인 모델의 뼈대를 생성한다.
- **WebSocket (socket.io-client)**: 상태 전이, 뇌관 에러, 고빈도 전류/전압 측정값 등 실시간으로 쏟아지는 이벤트를 수신한다.
- **데이터 합성 로직**:
  - 실시간으로 들어오는 고빈도 이벤트 데이터를 React State에 직접 꽂아 리렌더링을 매번 유발하지 않고, **`useRef` 메모리 공간에 버퍼링/누적**한다.
  - 정기적으로 또는 특정 이벤트 임계점 시점에 누적된 `useRef` 버퍼와 REST 스냅샷 데이터를 결합하여 **도메인 순수 함수(`deriveMonitoringPhase()`, `buildCellDetonatorStats()`)를 통해 상태 통계를 일괄 재계산**한 뒤 `setState`를 수행하여 가상 DOM 렌더링 성능을 보존한다.

---

## 3. WebSocket 라이프사이클 및 구독 누수 방지 (Listener Leak Prevention)

WebSocket은 단일 연결(싱글톤)을 앱 수명주기 전체에서 유지하되, 화면 전환(마운트/언마운트)에 따라 특정 이벤트를 동적으로 구독 및 해제해야 한다. 리스너 해제를 누락하면 **메모리 누수 및 중복 이벤트 콜백 실행 버거**가 발생하므로 엄격한 생명주기 제어가 필요하다.

### A. 중앙화된 싱글톤 소켓 관리
- `WebSocketService.ts`에서 글로벌 소켓 인스턴스 하나를 관리하며, 앱 진입부(`useAppWebSocketLifecycle.ts`)에서 단 1회 연결을 수행한다.

### B. 훅 기반의 임시 리스너 등록/해제
- 컴포넌트 마운트 시 `useWebSocketConfig`를 통해 이벤트 핸들러를 임시 등록하고, 언마운트(Cleanup) 시 반드시 고유 ID로 리스너를 파괴한다.

```typescript
// 예시: 실시간 이벤트 구독 수명주기 제어 패턴
useEffect(() => {
  const listenerId = 'progress-monitoring-status';
  
  // 1. 이벤트 리스너 임시 등록
  registerTemporaryListener(
    SocketEventNames.STATUS_EVENT,
    (data) => {
      // useRef 버퍼에 누적 후 재계산
      statusRef.current = data;
      recomputeAndSetState();
    },
    listenerId
  );

  // 2. Cleanup 함수에서 반드시 리스너 해제 (구독 누수 방지)
  return () => {
    unregisterTemporaryListener(listenerId);
  };
}, []);
```

---

## 4. 도메인 분리 설계 (Domain Layer Separation)
상태 계산 및 대용량 목록 가상화 필터링 등의 연산 로직은 React Hook이나 컴포넌트에 포함하지 않고 `domain/` 하위의 **순수 함수(Pure Functions)**로 격리하여 유닛 테스트 가능하게 설계한다.
- **UI/Hook**: 데이터의 비동기 수신, 이벤트 바인딩 등 부수효과(Side Effects) 처리.
- **Domain**: 수신된 원시 데이터를 기반으로 비즈니스 통계 파생 및 불변성 필터링 수행.

---

## 5. 네트워크 통신 방식별 멘탈 모델 및 아키텍처 비교 (Mental Models & Comparisons)

비동기 데이터 패치 및 실시간 이벤트 스트림 설계 시 혼동하기 쉬운 개념들을 **요청 시작권(Initiator)**과 **통로의 통신 방향(Directionality)** 축을 기준으로 정리한다.

### A. 요청 및 통신 채널 비교 매트릭스

| 통신 방식 | 요청 시작권 (Initiator) | 통로 방향 (Directionality) | 동작 성격 및 주 용도 |
|---|---|---|---|
| **REST (HTTP GET)** | **클라이언트만** 시작 | **N/A** (단발성 Request-Response) | 단발성 API 호출. 1회성 스냅샷 조회용. 반복적인 폴링(Polling)은 지양하는 것이 관례. |
| **SSE (Server-Sent Events)** | **서버가** 주도 가능 (Push) | **단방향** (서버 ➔ 클라이언트) | 읽기 전용 구독 통로. 상태가 변경되었음을 알리는 "방아쇠(Trigger)" 알림용. |
| **WebSocket (WS)** | **서버/클라이언트 양자** 주도 가능 | **양방향** (서버 ↔ 클라이언트) | 지속적인 TCP 커넥션 상에서 고빈도 센서 데이터 스트리밍 및 제어 명령 전송용. |

### B. 일상적 비유를 통한 이해 (The Telephony Metaphor)
- 📞 **REST GET (전화 걸기)**: 궁금한 것이 생길 때마다 상대방(서버)에게 전화를 걸어 답만 짧게 듣고 즉시 끊는 방식. 물어볼 때마다 전화를 새로 걸어야 하는 비용 발생 (Client-driven Pull).
- 📻 **SSE (라디오 방송)**: 라디오 채널을 틀어두면 방송국(서버)이 일방적으로 흘려보내는 뉴스를 계속 듣는 방식. 나는 방송국에 이 채널로 대답을 보낼 수 없음 (Server-driven Single-direction Push).
- 💬 **WebSocket (전화 연결 유지)**: 상대방과 전화를 건 채 끊지 않고 수화기를 계속 들고 있는 방식. 양쪽 모두 침묵하고 있다가도 아무 때나 먼저 말을 꺼낼 수 있음 (Bi-directional Stateful Push Stream).

### C. Kotlin Flow, MQTT Pub/Sub과의 연계 학습
- **개념적 동일성**: Kotlin/Android 개발 시의 LiveData `observe()`나 Flow `collect()`를 통해 상태 변화를 받아 처리하는 것, 그리고 MQTT 브로커의 특정 Topic을 `subscribe()`하는 것과 **"구독(Subscription) ➔ 이벤트 푸시(Push) ➔ 콜백(Callback) 실행"**의 멘탈 모델은 100% 동일하다.
- **프로토콜 차이**: MQTT는 중간 중재자(Broker)를 두고 계층형 Topic 필터링을 지원하는 다대다 통신 구조인 반면, 이 프로젝트의 웹소켓은 Socket.io 프로토콜을 이용해 클라이언트와 애플리케이션 서버 간 1:1 영구 채널을 열고 리스너(`registerTemporaryListener`)를 직접 꽂아 양방향으로 메시지를 주고받는다.

---

## 6. 코드베이스 실증 감사와 프로젝트 특화 관례 (Codebase Auditing & Project Idioms)

실제 코드를 개정하거나 기존 패턴에 맞추기 위해 리팩토링할 때는 단순히 문서나 일반적인 이론(Best Practice)에 의존하지 않고, **현재 코드베이스의 진실(Reality)**을 먼저 발굴하는 감사가 선행되어야 한다.

### A. Rule 0: 문서-코드 불일치 탐지 및 실증 교차검증 (Fact-Check First)
- **문서의 사멸 (Spec Drift)**: 설계 사양서나 API 가이드에 명시된 기술(예: SSE 호출 및 `/monitoring/events` 연결)이 실체 개발 과정에서 배제되거나 웹소켓 단일 구조로 대체되어, 실제 라우트 상에서는 미사용 사멸 코드(Dead Code)로 방치되는 사례가 흔히 발생한다.
- **실행 경로 역추적**: 코드 변경 전, 반드시 실제 구동되는 컴포넌트와 라우트에서 어떤 훅(`useViewerMonitoringBoard.ts`)과 파일들이 실제로 동작하고 있는지 정적 분석을 통해 역추적함으로써 잘못된 변경(사멸 코드 리팩토링 등)을 사전에 차단해야 한다.

### B. 교과서적 설계(Textbook) 대 프로젝트 특화 관례(Project Idiom)
- **교과서적 표준**: React Query (TanStack Query) 환경에서 GET 요청은 `useQuery`로 래핑하여 자동 캐싱 및 상태 동기화를 유도하는 것이 정석이다.
- **프로젝트 특화 표준**:
  - 이 프로젝트의 실시간 모니터링/제어 훅(예: `useArmRuntime.ts`)들은 **"최초 1회 수동 스냅샷 Fetch ➔ 이후 웹소켓 실시간 이벤트 누적"**의 수명주기를 따른다.
  - 이 경우 선언적 주기 호출과 자동 캐시 갱신을 수행하는 `useQuery`는 오히려 상태 동기화 충돌을 유발하므로, **`useMutation.mutateAsync`를 활용하여 GET 요청 스냅샷을 수동 비동기 호출하는 구조**를 프로젝트 표준으로 삼는다.
- **아키텍처 인사이트**: 이론상의 최적화 방식보다 **프로젝트 고유의 일치된 개발 규칙 및 관례(Consistent Idiom)**를 따르는 것이 코드의 파편화를 방지하고 협업의 일관성을 높이는 최선의 선택이 될 수 있다.


