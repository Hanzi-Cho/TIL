# TIL
Today I Learned

<!-- START_SECTION:learning_stats -->

## 📊 학습 트렌드 & 도메인 랭킹

| 🔥 최근 3개월 | 🏆 전체 누적 |
|:---:|:---:|
| ![](https://quickchart.io/chart?c=%7B%22type%22%3A%20%22doughnut%22%2C%20%22data%22%3A%20%7B%22labels%22%3A%20%5B%22%EB%8D%B0%EC%9D%BC%EB%A6%AC%22%2C%20%22%EB%8F%99%EC%8B%9C%EC%84%B1%22%2C%20%22%EB%84%A4%ED%8A%B8%EC%9B%8C%ED%81%AC%22%5D%2C%20%22datasets%22%3A%20%5B%7B%22data%22%3A%20%5B2%2C%202%2C%201%5D%2C%20%22backgroundColor%22%3A%20%5B%22%234F86C6%22%2C%20%22%23F4A261%22%2C%20%22%232A9D8F%22%5D%2C%20%22borderWidth%22%3A%202%7D%5D%7D%2C%20%22options%22%3A%20%7B%22plugins%22%3A%20%7B%22title%22%3A%20%7B%22display%22%3A%20true%2C%20%22text%22%3A%20%22%EC%B5%9C%EA%B7%BC%203%EA%B0%9C%EC%9B%94%22%2C%20%22fontSize%22%3A%2013%2C%20%22fontColor%22%3A%20%22%23333%22%7D%2C%20%22legend%22%3A%20%7B%22position%22%3A%20%22right%22%2C%20%22labels%22%3A%20%7B%22fontSize%22%3A%2011%2C%20%22boxWidth%22%3A%2012%7D%7D%2C%20%22datalabels%22%3A%20%7B%22display%22%3A%20false%7D%7D%2C%20%22cutoutPercentage%22%3A%2058%7D%7D&w=380&h=190&bkg=white) | ![](https://quickchart.io/chart?c=%7B%22type%22%3A%20%22doughnut%22%2C%20%22data%22%3A%20%7B%22labels%22%3A%20%5B%22%EB%8D%B0%EC%9D%BC%EB%A6%AC%22%2C%20%22%EB%8F%99%EC%8B%9C%EC%84%B1%22%2C%20%22%EB%84%A4%ED%8A%B8%EC%9B%8C%ED%81%AC%22%5D%2C%20%22datasets%22%3A%20%5B%7B%22data%22%3A%20%5B2%2C%202%2C%201%5D%2C%20%22backgroundColor%22%3A%20%5B%22%234F86C6%22%2C%20%22%23F4A261%22%2C%20%22%232A9D8F%22%5D%2C%20%22borderWidth%22%3A%202%7D%5D%7D%2C%20%22options%22%3A%20%7B%22plugins%22%3A%20%7B%22title%22%3A%20%7B%22display%22%3A%20true%2C%20%22text%22%3A%20%22%EC%A0%84%EC%B2%B4%20%EB%88%84%EC%A0%81%22%2C%20%22fontSize%22%3A%2013%2C%20%22fontColor%22%3A%20%22%23333%22%7D%2C%20%22legend%22%3A%20%7B%22position%22%3A%20%22right%22%2C%20%22labels%22%3A%20%7B%22fontSize%22%3A%2011%2C%20%22boxWidth%22%3A%2012%7D%7D%2C%20%22datalabels%22%3A%20%7B%22display%22%3A%20false%7D%7D%2C%20%22cutoutPercentage%22%3A%2058%7D%7D&w=380&h=190&bkg=white) |

<table><tr>
<td>

### 🔥 최근 3개월 집중 도메인

| 순위 | 도메인 | 커밋 | 비중 |
|:---:|:---|:---:|:---|
| 🥇 | **데일리 기록** | 2 | `█████░░░░░░░` 40.0% |
| 🥈 | **동시성/병렬** | 2 | `█████░░░░░░░` 40.0% |
| 🥉 | **네트워크** | 1 | `██░░░░░░░░░░` 20.0% |

</td>
<td>

### 🏆 전체 누적 학습 랭킹

| 순위 | 도메인 | 커밋 | 비중 |
|:---:|:---|:---:|:---|
| 🥇 | **데일리 기록** | 2 | `█████░░░░░░░` 40.0% |
| 🥈 | **동시성/병렬** | 2 | `█████░░░░░░░` 40.0% |
| 🥉 | **네트워크** | 1 | `██░░░░░░░░░░` 20.0% |

</td>
</tr></table>

> Github Actions을 통해 **2026년 06월 23일 15:30 (KST)** 에 자동으로 업데이트되었습니다.

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
