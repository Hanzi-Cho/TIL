"""
Analyzes git commit history by domain directory and updates README.md
with learning trend rankings (recent 3 months vs all-time).
"""

import json
import os
import re
import subprocess
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta, timezone

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

KST = timezone(timedelta(hours=9))
THREE_MONTHS_AGO = datetime.now() - timedelta(days=90)  # naive, for git date comparison

CHART_COLORS = ["#4F86C6", "#F4A261", "#2A9D8F", "#E76F51", "#A8DADC", "#9B59B6"]
MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

REPO_ROOT = os.path.dirname(README_PATH)


def get_knowledge_domains() -> set[str]:
    """Discover all current subdirectories under knowledge/ at runtime."""
    knowledge_path = os.path.join(REPO_ROOT, "knowledge")
    if not os.path.isdir(knowledge_path):
        return set()
    return {
        d for d in os.listdir(knowledge_path)
        if os.path.isdir(os.path.join(knowledge_path, d)) and not d.startswith(".")
    }


def get_domain(filepath: str, knowledge_domains: set[str]) -> str | None:
    """Return the knowledge subdomain for a file path, or None to skip."""
    parts = filepath.strip().split("/")
    # Only count files under knowledge/<domain>/
    if len(parts) >= 3 and parts[0] == "knowledge" and parts[1] in knowledge_domains:
        return parts[1]
    return None


def analyze_commits():
    knowledge_domains = get_knowledge_domains()

    cmd = ["git", "log", "--name-only", "--pretty=format:[%ad]", "--date=short"]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
    )

    recent: dict[str, int] = defaultdict(int)
    total: dict[str, int] = defaultdict(int)
    current_date: datetime | None = None

    for raw_line in result.stdout.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("["):
            try:
                current_date = datetime.strptime(line.strip("[]"), "%Y-%m-%d")
            except ValueError:
                pass
            continue
        domain = get_domain(line, knowledge_domains)
        if not domain:
            continue
        total[domain] += 1
        if current_date and current_date >= THREE_MONTHS_AGO:
            recent[domain] += 1

    return recent, total


def progress_bar(ratio: float) -> str:
    pct_int = round(ratio * 100)
    return f"![](https://geps.dev/progress/{pct_int})"


def make_donut_url(stats: dict[str, int], title: str) -> str:
    ranked = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:6]
    labels = [d for d, _ in ranked]
    data = [count for _, count in ranked]
    colors = CHART_COLORS[: len(data)]

    # Chart.js v2 syntax: title/legend go directly under options, NOT inside plugins
    config = {
        "type": "doughnut",
        "data": {
            "labels": labels,
            "datasets": [{"data": data, "backgroundColor": colors, "borderWidth": 2}],
        },
        "options": {
            "title": {"display": False},
            "legend": {
                "position": "right",
                "labels": {
                    "fontSize": 13,
                    "boxWidth": 14,
                    "fontColor": "#000000",
                    "fontStyle": "bold",
                },
            },
            "cutoutPercentage": 58,
        },
    }

    encoded = urllib.parse.quote(json.dumps(config, ensure_ascii=False))
    return f"https://quickchart.io/chart?c={encoded}&w=380&h=190&bkg=white"


def format_ranking_table(stats: dict[str, int], top_n: int = 5) -> str:
    if not stats:
        return "_기록된 학습 데이터가 없습니다._"

    ranked = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:top_n]
    total_sum = sum(stats.values())

    lines = [
        "| 순위 | 도메인 | 커밋 | 비중 |",
        "|:---:|:---|:---:|:---|",
    ]
    for rank, (domain, count) in enumerate(ranked, 1):
        medal = MEDALS.get(rank, str(rank))
        ratio = count / total_sum
        pct = ratio * 100
        lines.append(f"| {medal} | **{domain}** | {count} | {progress_bar(ratio)} {pct:.1f}% |")

    return "\n".join(lines)


def build_section(recent: dict[str, int], total: dict[str, int]) -> str:
    updated = datetime.now(KST).strftime("%Y년 %m월 %d일 %H:%M")

    recent_chart = make_donut_url(recent, "최근 3개월") if recent else None
    total_chart = make_donut_url(total, "전체 누적") if total else None

    if recent_chart and total_chart:
        chart_row = (
            "| 🔥 최근 3개월 | 🏆 전체 누적 |\n"
            "|:---:|:---:|\n"
            f"| ![]({recent_chart}) | ![]({total_chart}) |\n"
        )
    else:
        chart_row = ""

    recent_table = format_ranking_table(recent)
    total_table = format_ranking_table(total)

    # HTML table for side-by-side layout (blank lines needed for markdown inside <td>)
    side_by_side = (
        "<table><tr>\n"
        "<td>\n\n"
        "### 🔥 최근 3개월 집중 도메인\n\n"
        f"{recent_table}\n\n"
        "</td>\n"
        "<td>\n\n"
        "### 🏆 전체 누적 학습 랭킹\n\n"
        f"{total_table}\n\n"
        "</td>\n"
        "</tr></table>\n"
    )

    return (
        "\n"
        "## 📊 학습 트렌드 & 도메인 랭킹\n\n"
        f"{chart_row}\n"
        f"{side_by_side}\n"
        f"> Github Actions을 통해 **{updated} (KST)** 에 자동으로 업데이트되었습니다.\n"
    )


def update_readme():
    recent, total = analyze_commits()
    section = build_section(recent, total)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = (
        r"(<!-- START_SECTION:learning_stats -->)"
        r".*?"
        r"(<!-- END_SECTION:learning_stats -->)"
    )
    replacement = f"\\1\n{section}\n\\2"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README.md updated.")
    print(f"  Recent 3m : {dict(sorted(recent.items(), key=lambda x: -x[1]))}")
    print(f"  All-time  : {dict(sorted(total.items(), key=lambda x: -x[1]))}")


if __name__ == "__main__":
    update_readme()
