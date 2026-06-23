# TIL
Today I Learned

<!-- START_SECTION:learning_stats -->

## 📊 학습 트렌드 & 도메인 랭킹

### 🔥 최근 3개월 집중 도메인

| 순위 | 도메인 | 커밋 수 | 비중 |
|:---:|:---|:---:|:---|
| 🥇 | **데일리 기록** | 2 | `██████████████` 100% |
| 🥈 | **동시성/병렬** | 2 | `██████████████` 100% |
| 🥉 | **네트워크** | 1 | `███████░░░░░░░` 50% |

### 🏆 전체 누적 학습 랭킹

| 순위 | 도메인 | 커밋 수 | 비중 |
|:---:|:---|:---:|:---|
| 🥇 | **데일리 기록** | 2 | `██████████████` 100% |
| 🥈 | **동시성/병렬** | 2 | `██████████████` 100% |
| 🥉 | **네트워크** | 1 | `███████░░░░░░░` 50% |

> Github Actions을 통해 **2026년 06월 23일 15:18** 에 자동으로 업데이트되었습니다.


<!-- END_SECTION:learning_stats -->

## 구조

```
til/
├── daily/          # 날짜별 데일리 TIL (STAR 형식)
├── knowledge/      # 도메인·분야별 지식 정리
│   ├── aaos/
│   ├── cicd/
│   ├── concurrency/
│   ├── design-system/
│   └── network/
└── scripts/        # TIL 작성 보조 스크립트
    ├── create_template.py   # 오늘 날짜 STAR 템플릿 생성
    ├── generate_draft.py    # Gemini AI로 초안 생성
    └── update_readme.py     # 학습 통계 README 자동 갱신
```

## 스크립트 사용법

```bash
# 오늘 날짜 STAR 템플릿 생성
python scripts/create_template.py

# 자유 텍스트 → Gemini AI가 STAR 초안 작성
python scripts/generate_draft.py
python scripts/generate_draft.py path/to/notes.txt
```
