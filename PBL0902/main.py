import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / ".run-logs"
SERVICES = (
    ("APPX", "APPX.appx:app", 5000),
    ("MS1", "SiteA.MS1.ms1:app", 5051),
    ("MS2", "SiteA.MS2.ms2:app", 5052),
    ("MS3", "SiteB.MS3.ms3:app", 5053),
)


def stop_services(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main() -> int:
    LOG_DIR.mkdir(exist_ok=True)
    processes = []
    log_files = []
    try:
        for name, app, port in SERVICES:
            log_file = (LOG_DIR / f"{name}.log").open("a", encoding="utf-8")
            log_files.append(log_file)
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        app,
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(port),
                    ],
                    cwd=ROOT_DIR,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                )
            )

        print("Menjalankan PBL0902:")
        for name, _, port in SERVICES:
            print(f"{name}: http://127.0.0.1:{port}")
        print("Tekan Ctrl+C untuk menghentikan semua layanan.")

        while True:
            for (name, _, _), process in zip(SERVICES, processes):
                if process.poll() is not None:
                    print(
                        f"{name} berhenti (exit {process.returncode}); "
                        f"periksa {LOG_DIR / (name + '.log')}",
                        file=sys.stderr,
                    )
                    return 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPBL0902 dihentikan.")
        return 0
    finally:
        stop_services(processes)
        for log_file in log_files:
            log_file.close()


if __name__ == "__main__":
    raise SystemExit(main())
