# Maglev-Stream RN Lab: JS 브릿지 부하 실험 및 성능 벤치마크

> **React Native 브릿지 환경에서 메시지 전송 빈도 및 Payload 크기가 시스템 지연 시간(Delay)과 UI 렌더링에 미치는 영향 분석**

---

## 1. JS 브릿지 병목의 본질

React Native의 기존 브릿지 아키텍처에서 발생하는 성능 저하는 단순 데이터 총량(Total Bytes)뿐 아니라 다음과 같은 요소들의 조합으로 발생합니다.

$$\text{브릿지 부하} \approx \text{이벤트당 Payload 크기} \times \text{초당 Enqueue 횟수 (이벤트 빈도)}$$

*   **메시지 빈도(Frequency)**: 초당 메시지 처리 건수가 많아질수록 메시지 큐의 직렬화 오버헤드가 누적됩니다.
*   **직렬화 비용**: JSON 규격으로 데이터를 상호 파싱하고 바인딩할 때 메인 스레드(JS Thread) 점유 시간이 길어져 프레임 드랍이 유발됩니다.

---

## 2. 실험 환경 및 설계 구조

### A. 웹 플레이어 쉘 구조
*   **미디어 선택 및 재생**: `expo-document-picker`와 `expo-video` 조합을 사용하여 PC 웹 환경에서 로컬 비디오 파일을 선택하고 제어(재생/일시정지/재시작)할 수 있는 쉘 구현.
*   **실시간 지표 가시화**: 파일명, 포맷, 크기, 재생 상태 외에 Bytes/Event, Bytes/Sec, Events/Sec, Bridge Delay, Actual Delay, Video Play Delay, UI Render Delay, Packets Received 실시간 계측 디스플레이 탑재.

### B. 브릿지 랩(Bridge Lab) 구조
*   **Payload 일원화**: `src/bridge-lab/bridgePayloadCatalog.ts` 파일을 설계하여 다양한 실험용 데이터 구조와 대역폭 테스트용 데이터를 통합 제어.
*   **동적 부하 컨트롤**: UI에서 `dispatchEveryNFrames` 설정을 조절해 렌더링 프레임 주기당 네이티브 이벤트 주입 주기를 제어할 수 있도록 최적화.

---

## 3. 브릿지 부하 실측 벤치마크 (기본 80KB/event 기준)

80KB 크기의 페이로드를 사용하여 프레임당 전송 주기(N)에 따른 부하 및 지연 지표 실측 데이터입니다.

| 실험 조건 (80KB/event) | 이벤트 빈도 (Events/sec) | 전송 대역폭 (Bytes/sec) | Bridge Delay (ms) | Actual Delay (ms) | UI Render Delay (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **N = 11 (Low Load)** | ~ 4.0 events/sec | ~ 318 KB/sec | 4.3 ms | 5.9 ms | 1.1 ms |
| **N = 1 (High Load)** | ~ 29.5 events/sec | ~ 2.3 MB/sec | 5.3 ms | 7.8 ms | 2.1 ms |

### 결과 분석 및 해석
*   이벤트 주입 빈도를 7배 이상 가중시켰을 때 브릿지 딜레이와 렌더링 지연이 소폭 상승하는 양상을 보였습니다.
*   다만, 80KB 수준의 Payload에서는 아직 브릿지의 임계점 병목(UI 프리징)이 확실히 나타나지 않으므로, 추후 **1MB ~ 10MB 이상의 고부하 페이로드(예: RGBA Frame Slice)**를 가해 한계를 실측할 계획입니다.

---

## 4. 트러블슈팅 및 작업 정리

### A. 작업 경로 파편화 해소
*   **Symptom**: `D:\hanwhaproject\maglev-stream-rn`과 `D:\agentproject\wasm-native-bridge`로 분할되어 작업 폴더가 꼬여 있던 문제를 식별함.
*   **Solution**: 기존 Git 히스토리를 유지하기 위해 `wasm-native-bridge` 저장소를 기준으로 병합하고, 파편화된 소스 디렉토리를 정리함.

### B. VideoLabApp 컴포넌트 누락 복구
*   **Symptom**: `App.tsx` 구동 시 참조 대상인 `VideoLabApp` 모듈이 실제 프로젝트 내에 존재하지 않아 컴파일이 실패하고 플레이어가 동작하지 않음.
*   **Solution**: 로컬 파일 선택, 상태 표시 및 디버그 지표를 계측할 수 있는 최소 플레이어 쉘과 브릿지 랩 UI를 신규 이식하여 빌드 복구 완료.

### C. 8081 포트 충돌
*   **Symptom**: Expo 웹 서버 기동 시 `Port 8081 is already in use` 메시지와 함께 구동 실패.
*   **Solution**: 포트를 점유하고 있던 백그라운드 프로세스를 강제 종료하고 다시 웹 서버를 띄워 기동 완료.

### D. 미디어 데이터 획득의 구조적 제약 확인
*   **Symptom**: YouTube 등의 스트리밍 서비스는 브라우저 보안 정책(Same-Origin) 및 iframe 규격상 직접적인 비디오 프레임/오디오 데이터 추출이 전면 차단됨.
*   **Solution**: 실질적인 비전/음성 분석 AI 파이프라인 처리를 위해서는 로컬 파일 재생 소스를 주 통로로 설계하고, 데이터 추출과 재생 뷰를 격리하는 이원화 아키텍처 채택.
