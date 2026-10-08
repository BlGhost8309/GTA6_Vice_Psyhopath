# fill_from_markdown.py
"""
Заполняет дерево проекта кодом из new1.py и new2.py.

Запуск (в корне проекта, рядом с new1.py и new2.py):
    python fill_from_markdown.py

Скрипт ищет в этих файлах markdown-заголовки вида

    ### `path/to/file.py`

за которыми идёт блок ```python ... ``` — и пишет код в указанный файл.
Папки создаются автоматически. Непустые файлы перед перезаписью
сохраняются как <имя>.bak (пустые — просто перезаписываются).
"""
import re
import shutil
from pathlib import Path


HEADER_RE = re.compile(r'^#{1,6}\s+`([^`]+\.py)`\s*$', re.MULTILINE)
CODE_RE   = re.compile(r'```python\s*\n(.*?)\n```', re.DOTALL)


def extract_snippets(text):
    """Возвращает список (filename, code) из markdown-текста."""
    out = []
    for m in HEADER_RE.finditer(text):
        fname = m.group(1).strip()
        code_match = CODE_RE.search(text, m.end())
        if not code_match:
            print(f"  [warn] нет python-блока после `{fname}` — пропуск")
            continue
        out.append((fname, code_match.group(1)))
    return out


def main():
    root = Path(__file__).resolve().parent
    written, backed_up = 0, 0
    seen = set()

    for src_name in ("new1.py", "new2.py"):
        src = root / src_name
        if not src.exists():
            print(f"[SKIP] {src_name} не найден")
            continue

        text = src.read_text(encoding="utf-8")
        snippets = extract_snippets(text)
        print(f"[READ] {src_name}: блоков — {len(snippets)}")

        for fname, code in snippets:
            if fname in seen:
                print(f"  [dup]   {fname} — уже встречался, перезапишу")
            seen.add(fname)

            target = root / fname
            target.parent.mkdir(parents=True, exist_ok=True)

            # бэкапим только непустые файлы
            if target.exists() and target.read_text(encoding="utf-8").strip():
                bak = target.parent / (target.name + ".bak")
                shutil.copy2(target, bak)
                backed_up += 1
                print(f"  [bak]   {fname}  →  {bak.name}")

            target.write_text(code + "\n", encoding="utf-8")
            print(f"  [write] {fname}  ({len(code)} симв.)")
            written += 1

    print()
    print(f"Готово. Файлов записано: {written}, бэкапов: {backed_up}")
    print(f"Корень: {root}")


if __name__ == "__main__":
    main()