from argparse import ArgumentParser, Namespace
from pathlib import Path
from datetime import datetime


def parse_args(argv: list[str]) -> Namespace:
    parser = ArgumentParser(description="Outil simple de monitoring système")
    parser.add_argument("--interval", type=int, default=5, help="Intervalle entre deux mesures en secondes")
    parser.add_argument("--loops", type=int, default=1, help="Nombre de cycles. 0 = infini")
    parser.add_argument("--output", type=str, default="reports/system_report.txt", help="Fichier de rapport")
    parser.add_argument("--disk-path", type=str, default="C:\\", help="Chemin à analyser pour le disque")
    parser.add_argument("--cpu-threshold", type=float, default=80.0, help="Seuil CPU en %")
    parser.add_argument("--ram-threshold", type=float, default=80.0, help="Seuil RAM en %")
    parser.add_argument("--disk-threshold", type=float, default=80.0, help="Seuil disque en %")
    return parser.parse_args(argv)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def now_string() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
