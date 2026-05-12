# reporter.py
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

REPORT_DIR = "logs"
REPORT_FILE = os.path.join(REPORT_DIR, "report.txt")

def _label(value: float, threshold: int) -> str:
    if value >= threshold:
        return f"{value}% A (critique)"
    return f"{value}% (normal)"

def format_status(cpu: float, ram: float, disk: float, thresholds: dict) -> str:
    """Formate le rapport texte lisible."""
    lines = [
        "===== RAPPORT SYSTEME =====",
        f"Date : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"CPU : {_label(cpu, thresholds.get('cpu', 80))}",
        f"RAM : {_label(ram, thresholds.get('ram', 85))}",
        f"Disque : {_label(disk, thresholds.get('disk', 90))}",
        "",
        "Recommandations :",
        "- Vérifier les processus actifs",
        "- Libérer de l'espace disque",
    ]
    # Ajout d'une section anomalies détectées
    anomalies = []
    if cpu >= thresholds.get("cpu", 80):
        anomalies.append("Surcharge CPU détectée")
    if ram >= thresholds.get("ram", 85):
        anomalies.append("RAM saturée détectée")
    if disk >= thresholds.get("disk", 90):
        anomalies.append("Disque plein détecté")
    if anomalies:
        lines.insert(5, "Anomalies détectées : " + "; ".join(anomalies))
    return "\n".join(lines)

def write_report(text: str, path: str = REPORT_FILE) -> None:
    """Écrit le rapport dans logs/report.txt en créant le dossier si besoin."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info("Rapport écrit dans %s", path)
    except Exception:
        logger.exception("Erreur écriture rapport")

