# 크로스플랫폼 프레임워크별 아키텍처 및 트레이드오프 분석

> 은탄환(Silver Bullet)은 없다. 아키텍처의 완성도는 비즈니스의 규모, 성능 제약, 그리고 플랫폼과의 결합도 사이의 트레이드오프 조율에서 나온다.

본 문서는 현대 모바일/웹 크로스플랫폼 아키텍처의 핵심 축인 **React Native, Flutter, WASM(WebAssembly), .NET(C#), 그리고 Kotlin Multiplatform (KMP/CMP)**의 렌더링 파이프라인, 런타임 성능 구조, 그리고 대규모 엔터프라이즈 서비스 구축 시의 적합성을 깊이 있게 비교 분석한다.

---

## 1. 프레임워크별 렌더링 및 실행 구조 요약

| 비교 항목 | React / React Native | Flutter | WASM 기반 UI (Figma 등) | Kotlin Multiplatform (KMP) |
|---|---|---|---|---|
| **렌더링 주체** | 호스트 환경 (브라우저 DOM / OS 네이티브 뷰) | 자체 그래픽 엔진 (Impeller / Skia) | 웹 브라우저 내 `<canvas>` (WebGL/WebGPU) | 각 플랫폼 네이티브 UI (Compose/SwiftUI) |
| **핵심 통신 구조** | JS-Native Bridge 또는 JSI (C++ direct reference) | 없음 (C++ 엔진이 캔버스에 직접 픽셀 드로잉) | 샌드박스 내부 Wasm 연산 $\rightarrow$ GPU 그래픽 명령 직결 | 없음 (코틀린 코드가 플랫폼 네이티브 바이너리로 직접 컴파일) |
| **메모리 관리** | JS 엔진 가비지 컬렉션 (GC) | Dart VM 가비지 컬렉션 (GC) | Wasm 메모리 선형 관리 / Wasm GC | Android: JVM GC / iOS: Apple ARC 호환 |
| **웹(Web) 호환성** | 웹 네이티브 (HTML/CSS/JS) | WebAssembly + CanvasKit (무거운 초기 구동) | WebAssembly + CanvasKit/WebGPU | Kotlin/Wasm + Skia |

---

## 2. 런타임 병목 구조: 브릿지(직렬화) vs 다이렉트 렌더링

### ① React / React Native: 브릿지 탈피와 JSI의 도입
과거 React Native의 가장 큰 성능 병목은 **JSON 직렬화(Serialization) 기반의 Bridge**였다. JS 레이어와 네이티브 레이어가 데이터를 주고받기 위해 매번 JSON으로 변환하는 과정에서 CPU 자원이 낭비되었고, 초당 60프레임이 필요한 애니메이션이나 스크롤에서 성능 저하가 발생했다.

이를 극복하기 위해 도입된 **JSI (JavaScript Interface)** 아키텍처는 다음과 같다:
* **구조:** JavaScript 엔진이 네이티브 C++ 객체의 메모리 주소(참조)를 직접 공유한다.
* **효과:** 직렬화 비용이 완전히 **Zero**가 되어, JS 레이어에서 네이티브 함수를 동기적으로 직접 호출(Synchronous Direct Call)할 수 있게 되었다. 이로 인해 런타임 성능 격차가 대폭 감소하였다.

### ② Flutter: 다이렉트 렌더링과 웹 환경의 극복
Flutter는 OS의 위젯을 쓰지 않고 화면의 모든 픽셀을 자체 그래픽 엔진(Impeller/Skia)으로 직접 그린다. 

* **런타임 효율:** 단일 Dart VM 가상 머신 내에서 UI 로직 연산과 렌더링 파이프라인 처리가 동시에 일어나므로 직렬화 및 통신 비용이 없다.
* **초기 로딩 한계:** 웹 환경에서 Flutter는 C++ 엔진과 Dart 런타임 전체를 Wasm 바이너리로 다운로드해야 하므로 초기 구동이 무겁다는 치명적인 약점이 있었다.
* **Wasm GC 표준 지원:** 모던 브라우저가 **Wasm GC(Garbage Collection)** 프로토콜을 내장하면서 자체 메모리 관리 코드가 패키지에서 제외되었고, 이로 인해 다운로드 용량이 절반 이하로 줄어 초기 기동 속도가 비약적으로 향상되고 있다.

---

## 3. WASM 기반 UI의 의의와 샌드박스의 제약

WASM과 그래픽 API(WebGL/WebGPU)를 활용해 HTML/CSS를 전혀 거치지 않고 화면을 직접 그리는 방식은 플랫폼 독립적인 완벽한 UI(Pixel-Perfect)와 초고속 성능을 보장하는 궁극의 크로스플랫폼 기술이다. 대표적으로 **피그마(Figma)**가 C++/Rust 코드를 WASM으로 빌드하여 브라우저 내에서 직접 픽셀을 뿌리는 방식으로 대성공을 거두었다.

그러나 **대규모 비즈니스 서비스** 관점에서는 치명적인 제약이 따른다:
* **샌드박스(Sandbox)의 감옥:** WASM은 엄격한 보안 샌드박스 내부에서 실행된다. 이로 인해 OS 커널 하드웨어(블루투스, GPS, 카메라 픽셀 데이터, 보안 키스토어/Secure Enclave 등)에 직접 접근이 불가능하다.
* **글루 코드(Glue Code)의 복잡성:** 하드웨어 센서나 모바일 특화 API를 사용하려면 브라우저/네이티브의 JS 브릿지와 같은 접착용 코드를 이중으로 구현해야 하므로 대규모 시스템 설계 시 아키텍처가 매우 비대해진다.

---

## 4. 대규모 엔터프라이즈 앱을 위한 비교 분석

대규모 트래픽을 처리하고 수많은 개발자가 협업해야 하는 대형 서비스에서는 단순 생산성 외에 **아키텍처의 확장성, 모듈화, 결합도 제어**가 결정적인 기준이 된다.

### ① RN / Flutter / C# / WASM / KMP 아키텍처 분석

| 프레임워크 | 대규모 서비스 시 발생하는 아키텍처적 병목 | KMP/CMP의 근본적인 극복 구조 |
|---|---|---|
| **React Native** | JS 싱글 스레드 런타임 특성으로 인한 무거운 백그라운드 연산(비동기 트래픽, 암호화 등) 시 UI 스레드 간섭 | **Kotlin Coroutines / Flow** 기반의 구조적 동시성으로 스레드와 UI 레이어가 메모리/실행 단위에서 완벽히 격리됨. |
| **Flutter** | 거대 단일 엔진(Dart VM) 종속성으로 인해 물리적 하드웨어 수준의 모듈화가 불가능하며 변경 시 전체 영향도 계산이 큼 (Vendor Lock-in). | 프레임워크가 아닌 SDK로 동작하며, 공유 모듈이 각 플랫폼 표준 라이브러리(**`.aar`**, **`.framework`**)로 독립 빌드 및 캐싱됨. |
| **C# (.NET MAUI)** | 모바일 환경에서 Mono GC(가비지 컬렉터) 작동 시 발생하는 일시적 스레드 멈춤(Stop-the-world) 현상으로 미세한 렉 유발. | iOS 빌드 시 가상 머신이나 무거운 런타임 GC가 전혀 없이 **Apple ARC와 100% 호환**되도록 컴파일타임에 메모리 코드가 주입됨. |
| **WASM UI** | 시스템 접근성 및 OS 특화 API 연동 시 샌드박스 제약으로 인한 복잡한 가교(Glue) 아키텍처 양산. | **`expect`/`actual`** 선언을 통해 브릿지나 웹소켓 없이 양 플랫폼의 로우레벨 OS API를 다이렉트로 결합 가능. |

---

## 5. 아키텍트의 최종 선택: KMP + Native UI (Compose / SwiftUI)

백지상태에서 글로벌 단위의 대규모 서비스를 크로스플랫폼으로 설계한다면, 화면까지 공유하는 CMP보다는 **KMP를 통한 로직 공통화와 플랫폼별 표준 UI 프레임워크(Jetpack Compose / SwiftUI)의 이원화 결합**이 아키텍처상 최선이다.

```
┌──────────────────────────────────────────────────────────────┐
│                  UI Layer (주기적 변경 영역)                 │
│    Android: Jetpack Compose    │       iOS: SwiftUI          │
└──────────────────────────────┬───────────────────────────────┘
                               │ (UDF: 단방향 데이터 흐름)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│              Domain & Data Layer (KMP 공유 모듈)             │
│    Pure Kotlin (Coroutines, Flow, Ktor, SQLDelight 등)       │
└──────────────────────────────┬───────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    OS Platform Kernel API                    │
└──────────────────────────────────────────────────────────────┘
```

### 아키텍처적 선정 이유:
1. **관심사의 분리 (Separation of Concerns):** UI 프레임워크의 변동성과 생명주기(Lifecycle)로부터 핵심 비즈니스 로직을 완벽히 격리한다.
2. **초점 모듈화 (Ultra Multi-Module):** 수백 개의 기능 모듈을 독립적으로 캐싱 및 빌드(Incremental Build)할 수 있어 대규모 팀의 빌드 병목을 완전히 해소한다.
3. **무오버헤드 (Zero Overhead):** 런타임 가상 머신 없이 네이티브 언어 스펙으로 변환되어 메모리 점유율 최소화 및 네이티브 하드웨어 성능을 100% 보장한다.
4. **풀스택 시너지 (Full-Stack Kotlin):** 서버 백엔드(Spring Boot / Ktor)와 클라이언트 간 DTO 모델 및 비즈니스 검증 규칙을 코드 한 줄의 수정 없이 그대로 공유할 수 있어 싱크 미스로 인한 휴먼 에러를 방지한다.

---

## 관련 개념
* JSI (JavaScript Interface) & TurboModules
* WebAssembly GC (Wasm Garbage Collection)
* Impeller & Skia rendering pipeline
* Kotlin Native Compiler & LLVM
* Modular Architecture & Incremental Compilation

## 관련 문서
* [[platform-design-principles-kotlin]] — Kotlin 플랫폼 개발 원칙
* [[platform-design-principles-rn]] — React Native 플랫폼 개발 원칙
