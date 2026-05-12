from __future__ import annotations

import os
import platform
import shutil
import subprocess
from typing import Dict, List, Tuple


def _is_windows() -> bool:
    return os.name == "nt"


def _read_proc_stat() -> Tuple[int, int]:
    with open("/proc/stat", "r", encoding="utf-8") as f:
        first_line = f.readline()

    parts = first_line.split()
    if not parts or parts[0] != "cpu":
        raise RuntimeError("Unable to read CPU stats from /proc/stat")

    values = [int(x) for x in parts[1:]]
    idle_time = values[3] + values[4] if len(values) > 4 else values[3]
    total_time = sum(values)
    return idle_time, total_time


def _run_command(command: List[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _parse_key_value_lines(text: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def get_cpu_usage(snapshot_only: bool = False, previous_snapshot: Tuple[int, int] | None = None) -> Dict[str, object]:
    if _is_windows():
        if snapshot_only:
            return {"snapshot": None}

        output = _run_command(["wmic", "cpu", "get", "loadpercentage", "/value"])
        data = _parse_key_value_lines(output)
        percent = float(data.get("LoadPercentage", 0))
        return {"percent": round(percent, 2), "snapshot": None}

    current_snapshot = _read_proc_stat()

    if snapshot_only:
        return {"snapshot": current_snapshot}

    if previous_snapshot is None:
        raise ValueError("previous_snapshot is required when snapshot_only is False")

    prev_idle, prev_total = previous_snapshot
    curr_idle, curr_total = current_snapshot

    total_delta = curr_total - prev_total
    idle_delta = curr_idle - prev_idle

    if total_delta <= 0:
        percent = 0.0
    else:
        percent = (1.0 - (idle_delta / total_delta)) * 100.0

    return {"percent": round(percent, 2), "snapshot": current_snapshot}


def get_memory_usage() -> Dict[str, float]:
    if _is_windows():
        output = _run_command(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/Value"])
        data = _parse_key_value_lines(output)

        total_kb = int(data.get("TotalVisibleMemorySize", "0"))
        free_kb = int(data.get("FreePhysicalMemory", "0"))
        used_kb = total_kb - free_kb
        percent = (used_kb / total_kb) * 100.0 if total_kb else 0.0

        return {
            "total_gb": round(total_kb / (1024 * 1024), 2),
            "used_gb": round(used_kb / (1024 * 1024), 2),
            "percent": round(percent, 2),
        }

    meminfo = {}
    with open("/proc/meminfo", "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.split(":", 1)
            meminfo[key.strip()] = value.strip()

    total_kb = int(meminfo["MemTotal"].split()[0])
    available_kb = int(meminfo.get("MemAvailable", meminfo["MemFree"]).split()[0])

    used_kb = total_kb - available_kb
    percent = (used_kb / total_kb) * 100.0 if total_kb else 0.0

    return {
        "total_gb": round(total_kb / (1024 * 1024), 2),
        "used_gb": round(used_kb / (1024 * 1024), 2),
        "percent": round(percent, 2),
    }


def get_disk_usage(path: str = "/") -> Dict[str, float]:
    usage = shutil.disk_usage(path)
    used = usage.used
    total = usage.total
    percent = (used / total) * 100.0 if total else 0.0

    return {
        "path": path,
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
        "percent": round(percent, 2),
    }


def analyze_status(
    cpu_percent: float,
    ram_percent: float,
    disk_percent: float,
    cpu_threshold: float = 80.0,
    ram_threshold: float = 80.0,
    disk_threshold: float = 80.0,
) -> Dict[str, object]:
    recommendations: List[str] = []

    cpu_status = "critique" if cpu_percent >= cpu_threshold else "normal"
    ram_status = "critique" if ram_percent >= ram_threshold else "normal"
    disk_status = "critique" if disk_percent >= disk_threshold else "normal"

    if cpu_status == "critique":
        recommendations.append("- Vérifier les processus actifs")
        recommendations.append("- Identifier les tâches qui consomment trop de CPU")

    if ram_status == "critique":
        recommendations.append("- Fermer les applications inutiles")
        recommendations.append("- Redémarrer les services trop gourmands")

    if disk_status == "critique":
        recommendations.append("- Libérer de l’espace disque")
        recommendations.append("- Supprimer les fichiers temporaires inutiles")

    if not recommendations:
        recommendations.append("- Aucun problème critique détecté")

    return {
        "cpu_status": cpu_status,
        "ram_status": ram_status,
        "disk_status": disk_status,
        "recommendations": recommendations,
    }
