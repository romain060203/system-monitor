# monitor.py
import platform
import subprocess
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def _parse_cpu_from_top(output: str) -> Optional[float]:
    try:
        # Exemple de ligne: "Cpu(s):  3.0%us,  1.0%sy,  0.0%ni, 95.7%id,  0.3%wa,  0.0%hi,  0.0%si,  0.0%st"
        for part in output.split(","):
            if "id" in part:
                idle = float(part.strip().split("%")[0])
                return round(100.0 - idle, 1)
    except Exception:
        logger.exception("Erreur parsing top CPU")
    return None

def get_cpu_usage() -> float:
    """Retourne l'utilisation CPU en pourcentage (0-100)."""
    try:
        if platform.system() == "Linux":
            try:
                out = subprocess.check_output(["top", "-bn1"], text=True, stderr=subprocess.DEVNULL)
                cpu = _parse_cpu_from_top(out)
                if cpu is not None:
                    return cpu
            except Exception:
                logger.debug("top non disponible ou parsing échoué, fallback")
        # Fallback: utiliser /proc/stat
        if platform.system() == "Linux":
            with open("/proc/stat", "r") as f:
                line = f.readline()
            parts = line.split()
            if parts[0].startswith("cpu"):
                vals = list(map(int, parts[1:]))
                idle = vals[3]
                total = sum(vals)
                # lecture instantanée approximative: on retourne 0 si impossible
                return 0.0 if total == 0 else round((1.0 - idle / total) * 100.0, 1)
    except Exception:
        logger.exception("Impossible de récupérer l'utilisation CPU")
    return 0.0

def _parse_meminfo(meminfo: str) -> Optional[float]:
    try:
        lines = meminfo.splitlines()
        info = {}
        for l in lines:
            if ":" in l:
                k, v = l.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])
        if "MemTotal" in info and ("MemAvailable" in info or ("MemFree" in info and "Buffers" in info and "Cached" in info)):
            total = info["MemTotal"]
            available = info.get("MemAvailable", info.get("MemFree", 0) + info.get("Buffers", 0) + info.get("Cached", 0))
            used_pct = round((1.0 - available / total) * 100.0, 1)
            return used_pct
    except Exception:
        logger.exception("Erreur parsing /proc/meminfo")
    return None

def get_ram_usage() -> float:
    """Retourne l'utilisation RAM en pourcentage (0-100)."""
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo", "r") as f:
                meminfo = f.read()
            parsed = _parse_meminfo(meminfo)
            if parsed is not None:
                return parsed
        # Fallback: utiliser shutil if psutil absent (shutil n'a pas pourcentage RAM)
    except Exception:
        logger.exception("Impossible de récupérer l'utilisation RAM")
    return 0.0

def get_disk_usage(path: str = "/") -> float:
    """Retourne l'utilisation disque en pourcentage pour le chemin donné."""
    try:
        total, used, free = shutil.disk_usage(path)
        if total == 0:
            return 0.0
        percent = round(used / total * 100.0, 1)
        return percent
    except Exception:
        logger.exception("Impossible de récupérer l'utilisation disque")
    return 0.0

    }
