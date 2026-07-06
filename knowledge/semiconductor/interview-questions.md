# 삼성전자 DS 직군 대비 반도체 및 컴퓨터 구조 핵심 면접 질문 10선

이 문서는 시스템 소프트웨어 엔지니어 관점에서 반도체 하드웨어의 특성과 컴퓨터 시스템 아키텍처의 연동성을 검증하기 위한 면접 질문들을 정리한 문서입니다.

---

### Q1. DRAM의 동작 원리와 성능 특성
* DRAM Cell의 물리적 구조와 데이터 조회 방식(Row / Column, Activate, Read, Precharge)에 대해 설명하세요.
* **꼬리 질문**: Row Buffer Hit가 발생하는 시나리오와 이것이 시스템 성능에 미치는 긍정적 영향은 무엇인가요?

### Q2. CPU 캐시 계층 구조와 지역성(Locality)
* Cache의 필요성을 L1, L2, L3 캐시 구조, Cache Line 크기, 그리고 지역성(Spatial/Temporal Locality) 관점에서 설명하세요.
* **꼬리 질문**: 다차원 배열 탐색 시 루프 제어 변수의 순서(행 우선 vs 열 우선)가 캐시 효율 및 성능에 어떤 차이를 발생시키나요?

### Q3. 가상 메모리(Virtual Memory) 관리 메커니즘
* 가상 메모리 시스템의 작동 방식(Virtual/Physical Address, Page Table, TLB, Page Fault)에 대해 설명하세요.
* **꼬리 질문**: 실제 물리 메모리(RAM) 용량보다 훨씬 큰 크기의 가상 메모리 주소 공간을 가상 환경에서 할당하고 안정적으로 구동할 수 있는 핵심 원리는 무엇인가요?

### Q4. CPU와 메모리 간의 연산 데이터 흐름
* CPU가 특정 연산 코드(예: `a = b + c;`)를 수행할 때 Register, Cache, DRAM 사이에서 데이터가 이동하는 하드웨어적 파이프라인 흐름을 차례대로 기술하세요.

### Q5. 메모리 오더링(Memory Ordering)과 메모리 장벽(Memory Barrier)
* 멀티스레드 환경에서 코드 상의 연산 순서(예: `data = 10; flag = true;`)가 하드웨어 컴파일러 및 아웃오브오더(Out-of-Order) 실행에 의해 다른 스레드에게 뒤바뀌어 보일 수 있는 하드웨어적 원인을 설명하세요.
* **꼬리 질문**: 이를 방지하기 위한 Memory Barrier(Fences)의 역할과 구현 원리는 무엇인가요?

### Q6. 저장장치(SSD vs HDD) 설계 사상 및 제어 아키텍처
* SSD와 HDD의 물리적 데이터 저장 메커니즘의 근본적 차이와 SSD 컨트롤러가 내부적으로 수행하는 기법들(NAND Flash, Block/Page 단위 쓰기, Wear Leveling, Garbage Collection)을 설명하세요.

### Q7. DMA(Direct Memory Access) 제어 방식
* DMA 인터페이스란 무엇이며 왜 시스템 설계 시 필수적으로 요구되나요? CPU 직접 복사(CPU Copy)와 대비되는 대용량 데이터 전송 효율성에 대해 설명하세요.

### Q8. 인터럽트(Interrupt) 처리 및 폴링(Polling) 기법
* 외부 디바이스 제어 시 인터럽트 방식과 폴링 방식의 동작 차이와 비용(Cost)을 비교하여 설명하세요.
* **꼬리 질문**: 하드 실시간(Hard Real-Time) 시스템 설계 시 예외 상황 제어 및 지연 보장을 위해 언제 의도적으로 폴링 방식을 채택해야 하나요?

### Q9. 반도체 미세 공정화가 소프트웨어 아키텍처에 미치는 영향
* 반도체 제조 공정(3nm, 5nm, 2nm 등)의 미세화 트렌드가 시스템 전력(Power), 발열(Thermal), 동작 클럭(Clock Speed Limit), 그리고 멀티코어 병렬성에 미치는 영향과 이로 인해 소프트웨어 개발자가 고려해야 하는 설계 제약을 논하세요.

### Q10. 시스템 메모리 병목 분석 및 프로파일링 기법
* 프로그램의 전반적인 반응 속도가 눈에 띄게 저하되었으나 CPU 사용률(Core Utilization)은 매우 낮게 나타나는 상황입니다. 시스템적인 관점에서 메모리 병목(Cache Miss, NUMA 비대칭 접근, Memory Bandwidth 포화, False Sharing, TLB Miss) 중 무엇부터 검사하고 프로파일링해야 할지 방법론을 제시하세요.
