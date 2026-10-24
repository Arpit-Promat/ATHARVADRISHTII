"""Inspect locally extracted crop-disease datasets without changing any files.

Run from the repository root:
    python scripts/inspect_crop_datasets.py

Paste the path to each extracted dataset root when prompted. The script counts
common image files in each folder and prints likely class folders.
"""
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def image_count(folder: Path) -> int:
    try:
        return sum(
            1 for item in folder.iterdir()
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS
        )
    except (PermissionError, OSError):
        return 0


def inspect_dataset(crop_name: str) -> None:
    raw = input(f"Enter full path to extracted {crop_name} dataset: ").strip().strip('"')
    root = Path(raw).expanduser()

    if not root.exists() or not root.is_dir():
        print(f"Folder not found: {root}\n")
        return

    print(f"\n--- {crop_name}: {root} ---")
    total = 0
    image_folders = 0

    for folder in sorted((root, *(p for p in root.rglob("*") if p.is_dir()))):
        count = image_count(folder)
        if not count:
            continue
        label = "." if folder == root else str(folder.relative_to(root))
        print(f"{label}: {count} images")
        total += count
        image_folders += 1

    print(f"Total images: {total}")
    print(f"Folders containing images: {image_folders}")
    if image_folders <= 1:
        print("Note: images may be in one folder; verify labels before training.")
    print()


def main() -> None:
    print("ATHARVADRISHTI crop dataset inspection")
    print("This script only reads folders; it does not move, rename, or upload files.\n")
    for crop in ("Wheat", "Paddy/Rice", "Sugarcane"):
        inspect_dataset(crop)
    print("Inspection complete. Review the printed folder names before training.")


if __name__ == "__main__":
    main()
