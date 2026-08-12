import os
from pathlib import Path
import subprocess
import sys

files: dict[str, str] = {}

def remove_dot(string: str):
    current = 0
    while string[current] == ".":
        current += 1
    return string[current:]

def main():
    for file in os.listdir():
        file_path = Path(file)
        if file_path.suffix == ".py":
            files[file] = file_path.read_text(encoding="UTF8")
            lines = files[file].splitlines()
            for i in range(len(lines)):
                tokenized = list(filter(lambda x: True, lines[i].split()))
                if len(tokenized) < 2:
                    continue
                if tokenized[0] in {"from", "import"}:
                    tokenized[1] = remove_dot(tokenized[1])
                lines[i] = " ".join(tokenized)
            file_path.write_text("\n".join(lines), encoding="UTF8")
    subprocess.run([sys.executable, "-m", "pytest"])
    for file in os.listdir():
            file_path = Path(file)
            if file_path.suffix == ".py":
                file_path.write_text(files[file], encoding="UTF8")

if __name__ == "__main__":
    main()