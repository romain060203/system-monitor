# src/main.py
import time
import logging
from monitor import get_cpu_usage, get_ram_usage, get_disk_usage
from reporter import format_status, write_report
from utils import setup_logging

# Configuration
THRESHOLDS = {"cpu": 80, "ram": 85, "disk": 90}
INTERVAL = 60  # secondes, configurable

def run_once():
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disk = get_disk_usage("/")
    report = format_status(cpu, ram, disk, THRESHOLDS)
    write_report(report)
    logging.info("Rapport généré: CPU=%s RAM=%s DISK=%s", cpu, ram, disk)

def main():
    setup_logging()
    logging.info("Démarrage du monitor système")
    try:
        while True:
            try:
                run_once()
            except Exception:
                logging.exception("Erreur lors d'une itération de monitoring")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        logging.info("Arrêt demandé par l'utilisateur")

if __name__ == "__main__":
    main()
