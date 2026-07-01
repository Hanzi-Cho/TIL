# TIL
Today I Learned

<!-- START_SECTION:learning_stats -->

## 📊 학습 트렌드 & 도메인 랭킹

<table width="100%">
<tr>
<th align="center" width="50%">🔥 최근 3개월</th>
<th align="center" width="50%">🏆 전체 누적</th>
</tr>
<tr>
<td align="center" width="50%"><img src="https://quickchart.io/chart?c=%7B%22type%22%3A%20%22doughnut%22%2C%20%22data%22%3A%20%7B%22labels%22%3A%20%5B%22aaos%22%2C%20%22design-system%22%2C%20%22react-native%22%2C%20%22concurrency%22%2C%20%22platform%22%2C%20%22safety%22%5D%2C%20%22datasets%22%3A%20%5B%7B%22data%22%3A%20%5B13%2C%2013%2C%203%2C%203%2C%202%2C%201%5D%2C%20%22backgroundColor%22%3A%20%5B%22%234F86C6%22%2C%20%22%23F4A261%22%2C%20%22%232A9D8F%22%2C%20%22%23E76F51%22%2C%20%22%23A8DADC%22%2C%20%22%239B59B6%22%5D%2C%20%22borderWidth%22%3A%202%7D%5D%7D%2C%20%22options%22%3A%20%7B%22title%22%3A%20%7B%22display%22%3A%20false%7D%2C%20%22legend%22%3A%20%7B%22position%22%3A%20%22right%22%2C%20%22labels%22%3A%20%7B%22fontSize%22%3A%2013%2C%20%22boxWidth%22%3A%2014%2C%20%22fontColor%22%3A%20%22%23000000%22%2C%20%22fontStyle%22%3A%20%22bold%22%7D%7D%2C%20%22cutoutPercentage%22%3A%2058%7D%7D&w=500&h=250&bkg=white" width="100%" /></td>
<td align="center" width="50%"><img src="https://quickchart.io/chart?c=%7B%22type%22%3A%20%22doughnut%22%2C%20%22data%22%3A%20%7B%22labels%22%3A%20%5B%22aaos%22%2C%20%22design-system%22%2C%20%22react-native%22%2C%20%22concurrency%22%2C%20%22platform%22%2C%20%22safety%22%5D%2C%20%22datasets%22%3A%20%5B%7B%22data%22%3A%20%5B13%2C%2013%2C%203%2C%203%2C%202%2C%201%5D%2C%20%22backgroundColor%22%3A%20%5B%22%234F86C6%22%2C%20%22%23F4A261%22%2C%20%22%232A9D8F%22%2C%20%22%23E76F51%22%2C%20%22%23A8DADC%22%2C%20%22%239B59B6%22%5D%2C%20%22borderWidth%22%3A%202%7D%5D%7D%2C%20%22options%22%3A%20%7B%22title%22%3A%20%7B%22display%22%3A%20false%7D%2C%20%22legend%22%3A%20%7B%22position%22%3A%20%22right%22%2C%20%22labels%22%3A%20%7B%22fontSize%22%3A%2013%2C%20%22boxWidth%22%3A%2014%2C%20%22fontColor%22%3A%20%22%23000000%22%2C%20%22fontStyle%22%3A%20%22bold%22%7D%7D%2C%20%22cutoutPercentage%22%3A%2058%7D%7D&w=500&h=250&bkg=white" width="100%" /></td>
</tr>
<tr>
<td width="50%">

| 순위 | 도메인 | 커밋 | 비중 |
|:---:|:---|:---:|:---|
| 🥇 | **aaos** | 13 | <img src="https://geps.dev/progress/35" width="80"> 35.1% |
| 🥈 | **design-system** | 13 | <img src="https://geps.dev/progress/35" width="80"> 35.1% |
| 🥉 | **react-native** | 3 | <img src="https://geps.dev/progress/8" width="80"> 8.1% |
| 4 | **concurrency** | 3 | <img src="https://geps.dev/progress/8" width="80"> 8.1% |
| 5 | **platform** | 2 | <img src="https://geps.dev/progress/5" width="80"> 5.4% |

</td>
<td width="50%">

| 순위 | 도메인 | 커밋 | 비중 |
|:---:|:---|:---:|:---|
| 🥇 | **aaos** | 13 | <img src="https://geps.dev/progress/35" width="80"> 35.1% |
| 🥈 | **design-system** | 13 | <img src="https://geps.dev/progress/35" width="80"> 35.1% |
| 🥉 | **react-native** | 3 | <img src="https://geps.dev/progress/8" width="80"> 8.1% |
| 4 | **concurrency** | 3 | <img src="https://geps.dev/progress/8" width="80"> 8.1% |
| 5 | **platform** | 2 | <img src="https://geps.dev/progress/5" width="80"> 5.4% |

</td>
</tr>
</table>

> Github Actions을 통해 **2026년 07월 02일 02:19 (KST)** 에 자동으로 업데이트되었습니다.

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
