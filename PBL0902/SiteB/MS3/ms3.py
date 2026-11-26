from pathlib import Path

from server.app_factory import create_service

ROOT_DIR = Path(__file__).resolve().parents[2]
app = create_service(ROOT_DIR / "SiteB" / "MS3" / "DB-B.db", "MS3")
