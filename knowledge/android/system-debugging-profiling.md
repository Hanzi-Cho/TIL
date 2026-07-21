# Android 시스템 디버깅/프로파일링 (dmesg · logcat · Systrace/Perfetto · AOSP 추적)

이 문서는 칩셋 벤더 System SW 직무의 일상 업무인 시스템 레벨 디버깅 채널과 프로파일링 도구, 그리고 AOSP 소스 추적 방법론을 정리한 지식 문서입니다.

> 관련 문서: [chipset-vendor-bsp-core](chipset-vendor-bsp-core.md)(콜스택/E2E 흐름), [android-graphics-display-pipeline](android-graphics-display-pipeline.md)(프레임 파이프라인)

---

## 1. 로그 채널의 계층 구조: logcat vs dmesg

| | logcat | dmesg |
| --- | --- | --- |
| 영역 | 유저 공간 (앱/프레임워크/HAL) | 커널 공간 (링 버퍼) |
| 소스 | `Log.d` / `ALOGD` → logd 데몬 | `printk` → 커널 링 버퍼 |
| 버퍼 | main / system / crash / events / radio | 단일 링 버퍼 (오래된 로그 유실) |
| 대표 용도 | ANR, 크래시, HAL 동작 로그 | 드라이버 초기화, 커널 패닉, OOM, HW 에러 |

- **dmesg**: 하드웨어 드라이버 초기화, 모듈 로딩, kernel panic backtrace, 메모리 에러 등 로우레벨 로그 출력 도구. `printk` 레벨(KERN_ERR 등)로 필터링, `/proc/kmsg`가 원천.
- **디버깅 순서 원칙**: 증상이 상위에서 보여도 **logcat(유저) → binder 트랜잭션 → dmesg(커널)** 순으로 내려가며 어느 경계에서 이상이 시작됐는지 격리.
- 부팅 실패 시에는 logcat 자체가 없음 → 시리얼 콘솔(UART)의 커널 로그가 유일한 채널.

## 2. Systrace / Perfetto — 시스템 전역 타임라인 추적

- **원리**: 커널 `ftrace`(스케줄러 이벤트) + 유저 공간 `atrace`(ATRACE_CALL 마커)를 하나의 시간축에 병합 — 스레드 스케줄링, VSYNC, Binder 호출, 프레임 생명주기를 마이크로초 단위로 시각화.
- **Perfetto**: Systrace의 후속 표준. 장시간 트레이싱, SQL 기반 쿼리(trace processor), 웹 UI(ui.perfetto.dev), 커스텀 데이터 소스 지원.
- **Jank 분석 실전 순서**:
  1. 드랍된 프레임의 VSYNC 슬롯 식별
  2. 해당 슬롯에서 앱 `doFrame` / RenderThread / SurfaceFlinger / HWC 중 어디가 예산(16.6ms/8.3ms)을 초과했는지 확인
  3. 초과 원인 하강 분석: 락 경합? Binder 대기? fence 대기? CPU 주파수(DVFS)? 코어 마이그레이션?
- **벤더 관점**: 커스텀 HAL/드라이버에 `ATRACE` 마커를 심어 자사 IP 블록의 소요 시간을 타임라인에 노출시키는 것이 최적화의 전제.

## 3. 콜스택 기반 크래시/행 분석

- **Java 레이어**: ANR trace(`/data/anr/`), `Thread.dumpStack()` — 메인 스레드가 무엇을 기다리는지.
- **Native 레이어**: tombstone(`/data/tombstones/`), `ndk-stack` / `addr2line`으로 심볼 복원, `debuggerd`.
- **Kernel 레이어**: dmesg의 panic/oops backtrace, `ramoops/pstore`(재부팅 후에도 남는 커널 로그).
- **핵심 역량**: 세 레이어의 스택을 이어 붙여 종단 인과를 구성 — 예: "ANR(Java) ← Binder 대기 ← HAL의 ioctl 블로킹 ← 드라이버 IRQ 미발생(dmesg)".

## 4. System Bottleneck & Latency 최적화 방법론

1. **측정 먼저**: 감이 아닌 트레이스로 — Perfetto 타임라인에서 예산 초과 지점 특정.
2. **경계 비용 의심**: JNI 직렬화, Binder 트랜잭션 크기, 시스템 콜 빈도, 메모리 복사(→ Zero-Copy 가능한가).
3. **하드웨어 자원 확인**: CPU 주파수/코어 배치(big.LITTLE), GPU/DPU 부하, 메모리 대역폭, 발열 스로틀링.
4. **수치로 검증**: 개선 전후 프레임 드랍률, p99 레이턴시, CPU 점유율 비교. 60/120Hz 유지가 최종 판정 기준.

## 5. AOSP Source Tree Tracking (Trace-to-Code)

- **목적**: 프레임워크 버그의 원인을 문서가 아닌 **소스 코드에서 직접** 규명하는 능력 — 벤더 엔지니어는 구글 코드와 자사 코드의 경계에서 일하므로 필수.
- **도구**: [cs.android.com](https://cs.android.com) (코드 검색), `repo`(멀티 git 관리), 태그/브랜치별 diff.
- **주요 진입점**:
  - 그래픽스: `frameworks/native/services/surfaceflinger/`
  - HAL 인터페이스: `hardware/interfaces/`
  - Binder: `frameworks/native/libs/binder/`
  - Car(AAOS): `packages/services/Car/`
- **실전 패턴**: 로그 메시지 문자열로 코드 검색 → 해당 함수의 호출 경로 역추적 → 조건 분기에서 자사 환경(HAL 반환값, prop 설정)과의 상호작용 확인.
