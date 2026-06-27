from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtGui import QGuiApplication

from modbus_app.branding import create_brand_pixmap


def save_asset(path: Path, image_format: str) -> None:
    pixmap = create_brand_pixmap(512)
    if not pixmap.save(str(path), image_format):
        raise RuntimeError(f"Failed to save {path.name} as {image_format}.")


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    save_asset(assets_dir / "creative_factory.png", "PNG")
    save_asset(assets_dir / "creative_factory.ico", "ICO")

    app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
