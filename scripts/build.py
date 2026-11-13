"""Packaging and release script for Music Master using PyInstaller on Windows."""

import os
import shutil
import subprocess
import sys


def build_release() -> None:
    print("=== MUSIC MASTER RELEASE PACKAGING BUILD ===")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    dist_dir = os.path.join(project_root, "dist")
    build_dir = os.path.join(project_root, "build")

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name=MusicMaster",
        "--paths=src",
        "main.py",
    ]

    print("Executing:", " ".join(pyinstaller_cmd))
    result = subprocess.run(pyinstaller_cmd)

    if result.returncode != 0:
        print(f"Build failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    print("\n[SUCCESS] Music Master packaged successfully to:", os.path.join(dist_dir, "MusicMaster"))


if __name__ == "__main__":
    build_release()
