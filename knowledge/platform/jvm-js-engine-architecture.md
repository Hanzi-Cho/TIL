# 가상 머신(JVM)과 JS 엔진의 동작 원리 및 신규 CPU 아키텍처 포팅 구조 (Runtime & JIT Porting)

## 1. Java: Write Once, Run Anywhere (WORA) 아키텍처

자바는 컴파일타임과 런타임의 책임을 분리하여 기기 독립성(Platform Independence)을 구현한다.

```
[Main.java] 
   │ (javac 컴파일러 - 정적 컴파일)
   ▼
[Main.class (Bytecode)] ── 표준 규격 중간 언어 (OS 독립적)
   │
   ▼
[JVM (Java Virtual Machine)] ── OS/CPU별 통역사 (OS 의존적)
   ├─ Class Loader & Runtime Data Areas (Memory)
   └─ Execution Engine (Interpreter + JIT Compiler)
   │
   ▼
[Native Machine Code] ── 실제 하드웨어 실행 (Windows/Linux/macOS, x86/ARM)
```

1. **바이트코드 (Bytecode)**
   - 개발자가 작성한 소스코드(`*.java`)는 기계어로 직접 번역되지 않고, JVM 표준 명세를 따르는 가상의 CPU 명령어 집합인 **바이트코드(`*.class`)**로 변환된다.
2. **JIT 컴파일러 (Just-In-Time Compiler)**
   - 초기 진입 시 인터프리터 방식으로 한 줄씩 바이트코드를 읽어가며 실행하되, 자주 실행되는 최적화 대상 코드 블록(Hotspot) 식별 시 이를 메모리 상에서 실시간으로 직접 기계어(Native Code)로 컴파일하여 캐싱한다.
3. **가상 머신의 의존성**
   - 자바 프로그램 자체는 완전히 기기 독립적이지만, 이를 번역하는 **JVM 자체는 특정 OS 및 CPU 아키텍처용(C++로 개발됨)으로 고도로 최적화된 기기 의존적 프로그램**이다. Oracle, Microsoft, Amazon, Google 등 글로벌 빅테크 진영이 각 플랫폼 빌드를 전담하여 개발자에게 배포한다.

---

## 2. JavaScript: Runtimes & JIT Engines

자바스크립트는 컴파일 단계를 거치지 않고 배포되는 텍스트 소스코드(`*.js`) 형태이며, 각 브라우저 및 Node.js 런타임 내부에 포함된 **JS 엔진**을 통해 실행 시점에 하드웨어 명령어로 번역된다.

```
[script.js (Source Code)]
   │
   ▼
[JS Engine (V8, JavaScriptCore, SpiderMonkey 등)] ── C++ 기반 통역 엔진
   ├─ Parser & AST (Abstract Syntax Tree)
   ├─ Ignition Interpreter (바이트코드 변환 및 실행)
   └─ TurboFan JIT Compiler (고성능 기계어 최적화 컴파일)
   │
   ▼
[Native Machine Code] ── CPU 실행
```

- **V8 엔진의 파이프라인 (Google Chrome / Node.js)**
  1. 소스코드를 파싱하여 AST를 생성한 뒤, **Ignition 인터프리터**를 통해 중간 바이트코드로 바꾼다.
  2. 프로파일러가 실행 빈도가 높은 핫스폿 코드를 감시하다가, 최적화가 가능하다고 판단되면 **TurboFan JIT 컴파일러**를 구동시켜 고성능 아키텍처 최적화 기계어로 재작성하여 런타임 성능 지연을 단축한다.
  3. 동적 언어 특성상 타입 가정이 깨지면 최적화 코드를 해제(Deoptimization)하고 다시 인터프리터 단계로 롤백한다.

---

## 3. 신규 CPU 아키텍처와 JIT Code Generator 포팅 (Porting)

x86 및 ARM 진영 외에 자체 CPU 명령어 집합(ISA)을 설계하는 기업(예: RISC-V 연합, 중국 Loongson 등)이나 특수 목적 가속기(NPU) 제조사가 시장에서 동작하려면 자바 및 자바스크립트 가상 머신이 자사 칩에서 돌아가야 한다.

이 가상 머신 이식 과정을 **포팅(Porting)**이라 하며, 포팅 전담 SW 팀이 직접 JIT 코드 생성기(Code Generator)를 자사 어셈블리어에 맞춰 코딩해야 한다.

### OpenJDK Hotspot 내부 아키텍처 포팅 구조
OpenJDK 소스코드 내 가상 머신(Hotspot) 핵심 엔진에는 하드웨어/CPU 아키텍처별 어셈블러 모듈이 폴더별로 완전히 분리되어 있다.

```plaintext
openjdk/src/hotspot/cpu/
├── x86/          # x86_64 CPU 어셈블리 생성 C++ 소스
├── aarch64/      # ARM 64-bit CPU 어셈블리 생성 C++ 소스
├── riscv/        # RISC-V 오픈소스 CPU용 JIT Code Gen (최근 병합)
└── loongarch/    # 중국 LoongArch 독자 CPU용 JIT Code Gen (최근 병합)
```

### 포팅 엔지니어가 수행하는 핵심 작업
1. **바이트코드 맵핑**: 자바/JS 바이트코드 명령어 1개당 자사 CPU가 지원하는 레지스터 및 바이너리 오피코드(Opcode) 매칭 테이블을 구현한다.
2. **호출 규약(Calling Convention) 구현**: 인수를 레지스터(예: a0, a1)에 얹어 넘기는 방식, 스택 포인터(sp) 복원 및 프레임 포인터(fp) 처리 등의 하드웨어 스펙을 맞춘다.
3. **TCK 검증**: 새로 구현한 JIT Jitter 및 메모리 배리어가 표준 Java Spec 및 메모리 가시성 일관성을 위반하지 않는지 테스트(TCK)하고 공식 메인 스트림 리포지토리에 Pull Request를 기증하여 표준 병합(Merge)을 완료한다.
