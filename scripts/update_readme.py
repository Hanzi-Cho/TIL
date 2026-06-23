"""
Analyzes git commit history by domain directory and updates README.md
with learning trend rankings (recent 3 months vs all-time).
"""

import os
import re
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
THREE_MONTHS_AGO = datetime.now() - timedelta(days=90)

IGNORE_DOMAINS = {"scripts", ".github", ".vscode", "img", "images", "assets"}

DOMAIN_LABELS = {
    "aaos": "AAOS (Android Auto)",
    "cicd": "CI/CD",
    "concurrency": "동시성/병렬",
    "design-system": "디자인 시스템",
    "network": "네트워크",
    "daily": "데일리 기록",
}


def get_domain(filepath: str) -> str | None:
    """Extract domain name from a file path."""
    parts = filepath.strip().split("/")
    if len(parts) < 2:
        return None

    if parts[0] == "knowledge" and len(parts) >= 3:
        return parts[1]

    if parts[0] == "daily":
        return "daily"

    # Legacy paths before knowledge/ restructure (e.g. concurrency/foo.md)
    if parts[0] not in IGNORE_DOMAINS and parts[0] != "README.md":
        if os.path.isdir(os.path.join(os.path.dirname(__file__), "..", parts[0])):
            return parts[0]

    return None


def analyze_commits():
    cmd = ["git", "log", "--name-only", "--pretty=format:[%ad]", "--date=short"]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        cwd=os.path.dirname(README_PATH),
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

        domain = get_domain(line)
        if not domain:
            continue

        total[domain] += 1
        if current_date and current_date >= THREE_MONTHS_AGO:
            recent[domain] += 1

    return recent, total


MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def bar(ratio: float, width: int = 14) -> str:
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def format_ranking(stats: dict[str, int], top_n: int = 5) -> str:
    if not stats:
        return "_기록된 학습 데이터가 없습니다._\n"

    ranked = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:top_n]
    max_count = ranked[0][1]

    lines = [
        "| 순위 | 도메인 | 커밋 수 | 비중 |",
        "|:---:|:---|:---:|:---|",
    ]
    for rank, (domain, count) in enumerate(ranked, 1):
        medal = MEDALS.get(rank, str(rank))
        label = DOMAIN_LABELS.get(domain, domain)
        ratio = count / max_count
        pct = ratio * 100
        lines.append(f"| {medal} | **{label}** | {count} | `{bar(ratio)}` {pct:.0f}% |")

    return "\n".join(lines) + "\n"


def build_section(recent: dict[str, int], total: dict[str, int]) -> str:
    updated = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    return (
        "\n"
        "## 📊 학습 트렌드 & 도메인 랭킹\n\n"
        "### 🔥 최근 3개월 집중 도메인\n\n"
        f"{format_ranking(recent)}\n"
        "### 🏆 전체 누적 학습 랭킹\n\n"
        f"{format_ranking(total)}\n"
        f"> Github Actions을 통해 **{updated}** 에 자동으로 업데이트되었습니다.\n"
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
    print(f"  Recent 3m domains: {dict(sorted(recent.items(), key=lambda x: -x[1]))}")
    print(f"  All-time domains:  {dict(sorted(total.items(), key=lambda x: -x[1]))}")


if __name__ == "__main__":
    update_readme()
