# AI 에이전트 기반 UI 개정 및 디자인 시스템 명세 검토 게이트 (Spec Review Gate & AI Workflow)

## 1. 개요
LLM/AI 에이전트를 프론트엔드 UI 수정 파이프라인에 투입할 때 가장 큰 위협은 **명세의 공백을 AI가 임의로 추정하여 코드를 창작(Hallucination)하는 문제**이다. 이를 차단하기 위해 `blaster-web` 프로젝트에서는 **단일 진실 출처(SSOT) 게이트 검증**과 **Phase 0~7 표준 이행 플로우**를 결합한 AI 가버넌스 프레임워크를 구축하였다.

---

## 2. 핵심 원칙 (Core Principles)

1. **유일한 구현 입력 (Single Source of Truth)**
   - AI 구현의 유일한 입력은 **검토 게이트(SPEC_CHECKLIST)를 전항목 PASS한 명세서 (`specs/*.md`)** 및 **토큰 정의 (`tokens.json`, `GUARDRAILS.md`)**뿐이다.
   - 피그마/Stitch 시안 및 이미지 파일은 **Phase 5 시각 QA 검증용**으로만 사용되며, 구현 단계(Phase 3)의 입력으로 직접 참조하는 것을 금지한다.

2. **명세 공백 추정 금지 (Zero Hallucination)**
   - 명세 항목 A~I 중 단 하나라도 빈칸(FAIL)이 존재하면 AI는 코드를 단 한 줄도 작성할 수 없다.
   - 미정 항목 발견 시 AI는 임의 추정 대신 **선택지가 포함된 질의 목록**을 사용자에게 반환하고 답변을 명세에 반영 후 착수한다.

3. **단계별 Exit Criteria 강제**
   - Phase 0(게이트 PASS) $\rightarrow$ Phase 1(diff 및 작업 분할) $\rightarrow$ Phase 2(사용자 계획 승인) $\rightarrow$ Phase 3(단위 구현 & 스크린샷 자가검증) $\rightarrow$ Phase 4(통합 e2e) $\rightarrow$ Phase 5(시각 QA) $\rightarrow$ Phase 6~7(보고/커밋/문서 동기화) 순서로 진행하며, 각 단계의 exit 산출물을 충족해야만 다음 단계로 전이한다.

---

## 3. 명세 검토 게이트 (SPEC_CHECKLIST A~I)

UI 개정 착수 전, 다음 9가지 도메인의 공백 유무를 전수 검토한다.

| 영역 | 게이트 항목 | 검토 내용 |
|---|---|---|
| **A. 레이아웃 구조** | A-1 ~ A-6 | 영역 분할, gap/padding 간격, 정렬, 스크롤 정책, 계층 트리의 모든 요소 인벤토리, 기존 컴포넌트 재사용 매핑 |
| **B. 토큰 매핑** | B-1 ~ B-7 | Hex 직접값 배제(Semantic/Component 토큰 100%), Radius, Border, Typography, Shadow, 조건부 스타일 분기표(빈칸 없음) |
| **C. 상태 전수 정의** | C-1 ~ C-6 | 인터랙션(hover/pressed/selected), 데이터(0값/에러/로딩/empty), 색+텍스트 병기, truncate/자릿수, 뷰/시스템 전이 시 상태 초기화/유지, 실시간 갱신과 선택 하이라이트 충돌 방지 |
| **D. 수치/텍스트 포맷** | D-1 ~ D-5 | 천 단위 콤마, 시간 포맷, 모든 라벨 문자열 원문 그대로(문구 창작 방지), 파생값 계산식 및 불일치 대응 정책 |
| **E. 데이터 바인딩** | E-1 ~ E-4 | 표시 필드 출처(API $\rightarrow$ Selector $\rightarrow$ Hook), 미제공 필드 방침, 실시간 갱신 주기, 대용량 스크롤/가상화 기준 |
| **F. 인터랙션/내비** | F-1 ~ F-4 | 클릭/선택 동작, 탭/페이지네이션 상태유지, 터치 타깃 $\ge 48\times48\text{px}$, 선택/해제 수명주기 전반 |
| **G. 뷰포트** | G-1 ~ G-2 | 1280x768 기준 스크롤 수납, 1920/360 대응 범위 명시 |
| **H. 안전 UX 불변** | H-1 ~ H-3 | 다단계 발파/ARM 확인 유지, ABORT 버튼 상시 노출, Detail Panel 상시 노출 (접힘 금지) |
| **I. 모션/피드백** | I-1 ~ I-2 | 애니메이션/트랜지션 명시(미사용도 명시), Pressed 터치 피드백 |

---

## 4. UI 개정 시 입력 항목 체계 (Total 12가지)

사용자가 AI에게 UI 개정을 지시할 때 누락 없이 전달해야 하는 입력 파라미터 구조는 다음과 같다:

1. **명령 헤더 3가지**: 대상 화면/명세 경로, QA용 시안 경로, 변경 범위 한 줄
2. **명세 내용 9가지**: SPEC_CHECKLIST의 게이트 A~I 영역별 명세 데이터

---

## 5. 실전 UI 수정 명세 템플릿 (`[확인 필요]` 사전 검증 패턴)

실제 서비스(`blaster-web` 모니터링 화면 등) 개정 시, 사용자가 12가지 입력 요소를 AI에게 전달하기 위해 사용하는 표준 작성 템플릿 구조다. `[확인 필요]` 마커를 포함시켜 코드 및 API 계약 선행 확인을 유도한다.

```markdown
# UI 수정 명세 (실전 작성본 템플릿)

0. 작업 지정
- 대상 화면 · 명세 경로: Blast Monitoring / docs/specs/blast-monitoring.md [확인 필요]
- 시안(QA용) 경로: docs/specs/assets/blast-monitoring/ [확인 필요 — 없으면 Phase 5 N/A]
- 변경 범위 (한 줄): 상단바 배치/타이머 제거, 좌측 그룹보드 뷰 토글 신설, 발파기 셀 레이아웃·상태표기 정정, 빈 셀 배경 처리, Error Detonator List ID 포맷 변경

A. 레이아웃 구조 (A-1 ~ A-6)
- A-1. 상단바 위치: 주황 뒤로가기 버튼 행 우측 연속 배치 (코드 반영 여부 먼저 확인) [확인 필요: 컴포넌트 경로]
- A-2. 상단바 표기 순서: plan이름 → groups → blasters (타이머 완전 삭제) [확인 필요: 타이머 훅/API 공유 범위]
- A-3. 최상단 토글: "Blast 전체보기" / "Group별로 보기" 신설 [확인 필요: 좌측 그룹보드 컴포넌트 경로]
- A-4. 셀 레이아웃: 인덱스/이름 풀-와이드 2줄 + 하단 2x2 그리드(state|current / delay|voltage) [확인 필요: JSX 구조 diff]

B. 토큰 매핑 (B-1 ~ B-7)
- B-1. 빈 셀 배경: 흰 배경 제거 → 그리드 배경색과 동일 처리 [확인 필요: semantic 배경 토큰명 및 흰색 적용 원인]
- B-2. Comm 단계 Current/Voltage: ARM 이전 미노출 문제 해결 및 명확 표기 [확인 필요: Comm 전용 토큰 또는 placeholder 유무]
- B-3. 폰트/자간: 2x2 그리드 재조정에 따른 폰트 수치 조정 [확인 필요]

C. 상태 전수 (C-1 ~ C-6)
- C-1. 뷰 토글 상태: Blast 전체보기(우측 Blast Overview), Group별로 보기(우측 Group Overview), 단일 셀 선택(Blaster 상세), 재클릭(Overview 복귀) [확인 필요: 초기 진입 기본 토글값]
- C-2. Comm 단계 데이터: ARM 이전 current/voltage 표기 활성화 (B-2와 연동)
- C-3. 빈 셀 상태: 데이터 없음 시 그리드 배경과 동일한 빈 공간 처리 (B-1과 연동)

D. 수치·텍스트 포맷 (D-1 ~ D-5)
- D-1. Error Detonator List ID: `0X` 접두사 제거 + HEX 8자리 온전히 표기 [확인 필요: 원본 API HEX 자릿수 및 0-padding/대소문자 규칙]

E. 데이터 바인딩 (E-1 ~ E-4)
- 타이머/Comm 단계 수치/Error ID 원본 API 필드 검증 [확인 필요: API 응답 필드 제공 여부]

F. 인터랙션·내비게이션 (F-1 ~ F-4)
- 셀 단일 선택/재클릭 해제 수명주기, 토글 전환 시 셀 선택 유지/초기화 정책 [확인 필요]

G. 뷰포트 (G-1 ~ G-2)
- 1280x768 2x2 그리드 셀 높이 초과 여부 확인 [확인 필요]

H. 안전 UX 불변 (H-1 ~ H-3)
- ABORT/Detail 패널 상시 노출 유지, Comm 표기 변경 시 안전 판단 로직 영향 유무 [확인 필요]
```

