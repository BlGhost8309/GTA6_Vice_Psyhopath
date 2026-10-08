#!/usr/bin/env python3
"""
tree_to_file.py — сохраняет дерево проекта в файл project_tree.txt

Использование:
    python tree_to_file.py                # текущая папка
    python tree_to_file.py /path/to/proj  # конкретная папка
    python tree_to_file.py -d 6           # глубина 6 (по умолчанию 6)
    python tree_to_file.py -o tree.txt    # своё имя файла
"""

import sys
import argparse
import fnmatch
from pathlib import Path
from datetime import datetime

JUNK_PATTERNS = [
    "__pycache__", "*.py[cod]", "*.pyo", "*.pyd",
    ".venv", "venv", "env", ".env",
    ".idea", ".vscode", "*.swp",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
    "*.egg-info", "build", "dist",
    ".DS_Store", "Thumbs.db",
    "*.log", "*.sqlite3", "*.db",
    "node_modules",
    ".ipynb_checkpoints",
    "*.egg", "*.whl",
]

HIDE_FROM_TREE = {".git"}
DEFAULT_DEPTH = 6
DEFAULT_OUTPUT = "project_tree.txt"


def load_gitignore_patterns(root: Path):
    patterns = []
    gi = root / ".gitignore"
    if gi.exists():
        with open(gi, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line.rstrip("/"))
    return patterns


def is_junk(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in JUNK_PATTERNS)


def is_ignored(name: str, patterns) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def build_tree(root: Path, max_depth: int):
    gitignored = load_gitignore_patterns(root)
    lines = []
    stats = {"dirs": 0, "files": 0, "junk": 0, "ignored": 0}

    lines.append(f"# Project tree: {root.resolve()}")
    lines.append(f"# Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"# .gitignore: {'found' if (root / '.gitignore').exists() else 'NOT FOUND'}")
    lines.append(f"# .git dir:   {'found' if (root / '.git').exists() else 'NOT FOUND'}")
    lines.append("")
    lines.append(f"{root.name or str(root)}/")

    def walk(path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        entries = [e for e in entries if e.name not in HIDE_FROM_TREE]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "
            name = entry.name
            mark = ""

            if entry.is_dir():
                stats["dirs"] += 1
                if is_junk(name):
                    mark = "   [JUNK -> add to .gitignore]"
                    stats["junk"] += 1
                elif is_ignored(name, gitignored):
                    mark = "   [already in .gitignore]"
                    stats["ignored"] += 1
                lines.append(f"{prefix}{connector}{name}/{mark}")
                walk(entry, prefix + extension, depth + 1)
            else:
                stats["files"] += 1
                if is_junk(name):
                    mark = "   [JUNK -> add to .gitignore]"
                    stats["junk"] += 1
                elif is_ignored(name, gitignored):
                    mark = "   [already in .gitignore]"
                    stats["ignored"] += 1
                try:
                    size = entry.stat().st_size
                except OSError:
                    size = -1
                lines.append(f"{prefix}{connector}{name} ({size} B){mark}")

    walk(root)

    lines.append("")
    lines.append("─" * 60)
    lines.append(f"dirs: {stats['dirs']}, files: {stats['files']}")
    lines.append(f"junk (NOT ignored): {stats['junk']}")
    lines.append(f"already ignored:    {stats['ignored']}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Сохраняет дерево проекта в файл")
    ap.add_argument("path", nargs="?", default=".", help="Путь к проекту")
    ap.add_argument("-d", "--depth", type=int, default=DEFAULT_DEPTH)
    ap.add_argument("-o", "--output", default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"❌ Путь не существует: {root}")
        sys.exit(1)

    text = build_tree(root, args.depth)
    out = Path(args.output)
    out.write_text(text, encoding="utf-8")
    print(f"✅ Готово: {out.resolve()}")
    print(f"   Кидай этот файл мне.")


if __name__ == "__main__":
    main()
