import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LOG_DIR = ROOT_DIR / ".run-logs"
VENV_DIR = ROOT_DIR / ".venv"

SERVICES = (
    ("APPX", ROOT_DIR / "APPX", "appx.py", "http://localhost:5000"),
    ("MS1", ROOT_DIR / "SiteA" / "MS1", "ms1.py", "http://localhost:5051/cars/"),
    ("MS2", ROOT_DIR / "SiteA" / "MS2", "ms2.py", "http://localhost:5052/cars/"),
    ("MS3", ROOT_DIR / "SiteB" / "MS3", "ms3.py", "http://localhost:5053/cars/"),
)


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def python_executable() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_environment() -> Path:
    python = python_executable()

    if not python.exists():
        print("Menyiapkan environment Python...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    requirements = ROOT_DIR / "requirements.txt"
    marker = VENV_DIR / ".requirements-installed"

    if not marker.exists() or marker.stat().st_mtime < requirements.stat().st_mtime:
        print("Menginstal dependency PBL0901...")
        subprocess.run(
            [str(python), "-m", "pip", "install", "-r", str(requirements)],
            check=True,
        )
        marker.write_text(requirements.read_text(encoding="utf-8"), encoding="utf-8")

    return python


def main() -> int:
    try:
        python = ensure_environment()
    except subprocess.CalledProcessError as error:
        print(f"Gagal menginstal dependency (kode keluar {error.returncode}).")
        return 1

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    processes: list[subprocess.Popen] = []
    log_files = []

    print("Menjalankan PBL0901...")

    try:
        for name, working_dir, script, _ in SERVICES:
            log_file = (LOG_DIR / f"{name}.log").open("a", encoding="utf-8")
            log_files.append(log_file)

            process = subprocess.Popen(
                [str(python), "-u", script],
                cwd=working_dir,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
            processes.append(process)

        for name, _, _, address in SERVICES:
            print(f"{name}: {address}")

        print()
        print("Tekan Ctrl+C untuk menghentikan semua layanan.")
        print(f"Log tersedia di {LOG_DIR}")

        while True:
            for (name, _, _, _), process in zip(SERVICES, processes):
                if process.poll() is not None:
                    print(
                        f"{name} berhenti dengan kode keluar {process.returncode}. "
                        f"Lihat log di {LOG_DIR / (name + '.log')}",
                        file=sys.stderr,
                    )
                    return 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPBL0901 dihentikan.")
        return 0
    finally:
        stop_processes(processes)
        for log_file in log_files:
            log_file.close()


if __name__ == "__main__":
    raise SystemExit(main())
