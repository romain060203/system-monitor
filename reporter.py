from pathlib import Path
from datetime import datetime


def build_report(
    cpu_percent: float,
    cpu_status: str,
    ram_percent: float,
    ram_status: str,
    disk_percent: float,
    disk_status: str,
    recommendations: list[str],
) -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "===== RAPPORT SYSTEME =====",
        f"Date : {today}",
        f"CPU : {cpu_percent}% ({cpu_status})",
        f"RAM : {ram_percent}% ({ram_status})",
        f"Disque : {disk_percent}% ({disk_status})",
        "Recommandations :",
    ]

    for item in recommendations:
        lines.append(item)

    lines.append("")
    return "\n".join(lines)


def save_report(report: str, output_path: Path) -> None:
    output_path.write_text(report, encoding="utf-8")
