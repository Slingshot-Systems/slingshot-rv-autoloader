import os
import re
import zipfile
from pathlib import Path

from rich import print
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn


def make_rv_package():
    # Define source and destination paths
    SRC_DIR = Path.cwd() / "src"
    BUILD_DIR = Path.cwd() / "build"
    PACKAGE_FILE = SRC_DIR / "PACKAGE"

    # Ensure build directory exists
    BUILD_DIR.mkdir(exist_ok=True)

    # Extract version from PACKAGE file
    version = "unknown"
    with open(PACKAGE_FILE, "r") as file:
        for line in file:
            if match := re.match(r"version:\s*(.+)", line):
                version = match[1].strip()
                break

    # Define output file name
    zip_filename = BUILD_DIR / f"slingshot_autoloader-{version}.rvpkg"

    # List of files to include in the zip
    files_to_zip = [
        SRC_DIR / "slingshot_autoloader.py",
        SRC_DIR / "slingshot_autoloader_config.py",
        SRC_DIR / "rv_menu_schema.py",
        SRC_DIR / "PACKAGE",
        SRC_DIR / "ocio" / "studio-config-v2.1.0_aces-v1.3_ocio-v2.2.ocio",
    ]

    # Create the zip package with progress bar
    with (
        zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf,
        Progress(
            TextColumn("[bold blue]Zipping:"),
            BarColumn(),
            TimeRemainingColumn(),
        ) as progress,
    ):
        task = progress.add_task("Compressing files...", total=len(files_to_zip))

        for file_path in files_to_zip:
            arcname = file_path.relative_to(SRC_DIR)
            zipf.write(file_path, arcname)
            progress.update(task, advance=1)

    print(f"[bold green]Packaged files into {zip_filename}[/bold green]")


if __name__ == "__main__":
    make_rv_package()
