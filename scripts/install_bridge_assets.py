"""Install the original bridge PNGs from the downloaded v0.8 update archive.

Usage: python3 scripts/install_bridge_assets.py
"""
from pathlib import Path
from zipfile import ZipFile
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "Downloads"
TARGET = ROOT / "levels" / "bridge" / "assets"
ARCHIVE = "afterglow_bridge_game_patch_v08.zip"

def main():
    candidates = [DOWNLOADS / ARCHIVE, ROOT / ARCHIVE]
    candidates += sorted(DOWNLOADS.glob("afterglow_bridge_game_patch_v08*.zip"), reverse=True)
    source = next((p for p in candidates if p.is_file()), None)
    if source is None:
        print("ZIP not found. Download afterglow_bridge_game_patch_v08.zip to ~/Downloads first.")
        sys.exit(1)
    prefix = "afterglow_bridge_game_patch_v08/levels/bridge/assets/"
    count = 0
    with ZipFile(source) as z:
        for item in z.infolist():
            if item.is_dir() or not item.filename.startswith(prefix):
                continue
            relative = Path(item.filename[len(prefix):])
            if ".." in relative.parts or relative.is_absolute():
                raise ValueError("Unsafe archive path")
            dest = TARGET / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as inp, dest.open("wb") as out:
                shutil.copyfileobj(inp, out)
            count += 1
    if count != 14:
        print(f"Extracted {count} files; expected 14. Check the ZIP contents.")
        sys.exit(1)
    print(f"Installed {count} graphics files into {TARGET}")
    print("Run: python3 main.py --scene bridge")

if __name__ == "__main__":
    main()
