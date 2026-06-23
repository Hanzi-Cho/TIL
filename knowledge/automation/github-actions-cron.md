# GitHub Actions & Cron — 자동화 및 스케줄 실행

## 1. Cron 표현식

```
┌─ 분 (0-59)
│  ┌─ 시 (0-23)
│  │  ┌─ 일 (1-31)
│  │  │  ┌─ 월 (1-12)
│  │  │  │  ┌─ 요일 (0-7, 0·7=일요일)
│  │  │  │  │
*  *  *  *  *
```

| 표현 | 의미 |
|---|---|
| `0 15 * * *` | 매일 UTC 15:00 = KST 00:00 |
| `0 9 * * 1` | 매주 월요일 KST 18:00 |
| `*/5 * * * *` | 5분마다 |
| `0 0 1 * *` | 매월 1일 자정 |

> **GitHub Actions cron은 UTC 기준**이다. KST(UTC+9)로 자정에 실행하려면 `0 15 * * *` 사용.


## 2. GitHub Actions 구조

```
.github/
└── workflows/
    └── my-workflow.yml   ← 트리거·잡·스텝 정의
```

```yaml
on:                        # 트리거 정의
  schedule:
    - cron: '0 15 * * *'  # 스케줄
  push:
    branches: [main]
    paths-ignore:          # 이 경로 변경은 무시
      - 'README.md'
  workflow_dispatch:       # 수동 실행 버튼 활성화

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write      # 레포에 커밋·푸시 허용

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # 0 = 전체 히스토리 (git log 분석 시 필수)

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run script
        run: python scripts/my_script.py

      - name: Commit and push if changed
        run: |
          git config user.name  'Hanzi-Cho'
          git config user.email 'whwogus1983@gmail.com'
          git diff --quiet && git diff --staged --quiet \
            || (git add README.md \
                && git commit -m "chore: auto-update [skip ci]" \
                && git push)
```

### 핵심 개념

| 개념 | 설명 |
|---|---|
| `on` | 워크플로우 트리거 조건 |
| `jobs` | 병렬 실행 단위. 각 job은 독립 가상머신 |
| `steps` | job 내부의 순차 실행 단계 |
| `uses` | 공개 Action 재사용 (`owner/repo@version`) |
| `run` | 쉘 명령어 직접 실행 |
| `permissions: contents: write` | 레포 파일 쓰기 권한 (기본은 read-only) |


## 3. 무한루프 방지 패턴

Actions가 커밋·푸시 → 다시 push 트리거 → 무한반복이 일어날 수 있다.

**방법 1: `paths-ignore`** — README.md 변경은 트리거에서 제외
```yaml
on:
  push:
    paths-ignore:
      - 'README.md'
```

**방법 2: `[skip ci]` 커밋 메시지** — GitHub이 인식해 워크플로우 스킵
```bash
git commit -m "chore: auto-update [skip ci]"
```

두 방법을 함께 쓰면 이중 안전장치가 된다.


## 4. 잔디(Contribution Graph) 조건

GitHub 기여 그래프에 커밋이 찍히려면:

1. 커밋 author 이메일이 GitHub 계정에 등록된 이메일과 일치해야 한다
2. 기본 브랜치(main)에 포함되어야 한다
3. fork가 아닌 본인 레포여야 한다

```yaml
# ❌ 잔디 안 깔림
git config user.name  'github-actions[bot]'
git config user.email 'github-actions[bot]@users.noreply.github.com'

# ✅ 잔디 깔림
git config user.name  'Hanzi-Cho'
git config user.email 'whwogus1983@gmail.com'  # GitHub 계정에 등록된 이메일
```


## 5. 무료 플랜 한도

| 구분 | 공개 레포 | 비공개 레포 |
|---|---|---|
| 실행 시간 | **무제한** | 월 2,000분 |
| 스토리지 | 500MB | 500MB |

매일 1회 실행 × 약 2분 = 월 60분 → 비공개도 무료 한도의 3%.


## 6. GitHub HTML Sanitizer 주의사항

GitHub README에 HTML을 삽입할 때 일부 속성은 sanitizer에 의해 제거된다.

| 태그 | 허용 속성 | 제거되는 속성 |
|---|---|---|
| `<table>` | `border`, `cellpadding`, `cellspacing` | **`width`** |
| `<td>`, `<th>` | `align`, `colspan`, `rowspan` | **`width`** |
| `<img>` | `src`, `alt`, `title`, **`width`**, **`height`** | `style` |

```markdown
<!-- ❌ 렌더링 시 width 제거됨 -->
<table width="100%">
<td width="50%">...</td>

<!-- ✅ img의 width는 허용 -->
<img src="..." width="80">
```

> `<td width>` 로 컬럼 너비를 제어하려는 시도는 동작하지 않는다.
> 너비 제어가 필요한 이미지는 반드시 `<img width>` 태그를 직접 사용해야 한다.
