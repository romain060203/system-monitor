from pathlib import Path
import sys
import time

from monitor import get_cpu_usage, get_memory_usage, get_disk_usage, analyze_status
from reporter import build_report, save_report
from utils import parse_args, ensure_parent_dir, now_string


def run() -> int:
    args = parse_args(sys.argv[1:])

    output_path = Path(args.output)
    ensure_parent_dir(output_path)

    print("System monitor started at", now_string())
    print(f"Report file: {output_path}")
    print(f"Interval: {args.interval}s | Loops: {args.loops if args.loops > 0 else 'infinite'}")
    print(f"Thresholds -> CPU: {args.cpu_threshold}% | RAM: {args.ram_threshold}% | Disk: {args.disk_threshold}%")
    print("-" * 60)

    try:
        previous_cpu = get_cpu_usage(snapshot_only=True).get("snapshot")

        loop_index = 0
        while True:
            if args.loops > 0 and loop_index >= args.loops:
                break

            time.sleep(args.interval)

            cpu = get_cpu_usage(previous_snapshot=previous_cpu)
            previous_cpu = cpu.get("snapshot")

            memory = get_memory_usage()
            disk = get_disk_usage(args.disk_path)

            status = analyze_status(
                cpu_percent=cpu["percent"],
                ram_percent=memory["percent"],
                disk_percent=disk["percent"],
                cpu_threshold=args.cpu_threshold,
                ram_threshold=args.ram_threshold,
                disk_threshold=args.disk_threshold,
            )

            report = build_report(
                cpu_percent=cpu["percent"],
                cpu_status=status["cpu_status"],
                ram_percent=memory["percent"],
                ram_status=status["ram_status"],
                disk_percent=disk["percent"],
                disk_status=status["disk_status"],
                recommendations=status["recommendations"],
            )

            save_report(report, output_path)
            print(report)
            print(f"[OK] Report written to {output_path}")
            print("-" * 60)

            loop_index += 1

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
