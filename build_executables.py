import subprocess
import os


def build_with_pyinstaller():
    platforms = {
        # TODO can also add --icon=icon.ico and
        "windows": ["--onefile", "--name", "dicomtag-win", "dicomtag/main.py"],
        "linux": ["--onefile", "--name", "dicomtag-linux", "dicomtag/main.py"]
    }

    for platform, args in platforms.items():
        print(f"Building for {platform}...")
        subprocess.run(["pyinstaller"] + args, check=True)
        print(f"Executable for {platform} built successfully.")


if __name__ == "__main__":
    build_with_pyinstaller()
