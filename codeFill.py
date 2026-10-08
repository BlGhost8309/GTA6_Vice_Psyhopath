# fill_from_markdown.py  (универсальная версия)
"""
Заполняет дерево проекта кодом из new1.py и new2.py.

Запуск (в корне проекта, рядом с new1.py и new2.py):
    python fill_from_markdown.py

Скрипт устойчив к тому, что при копировании из чата разметка потерялась:
заголовок может быть в виде
    ### `path/file.py`
    ## path/file.py
    **path/file.py**
    path/file.py
и даже без пустой строки перед блоком кода.

Порядок работы:
  1. Идём по строкам, отслеживаем состояние "внутри код-блока".
  2. Вне кода ищем ближайшую строку, похожую на имя .py-файла.
  3. Как только встретили ```python — запоминаем, что дальше идёт код
     для последнего найденного имени.
  4. По закрывающим ``` — сохраняем в файл.
"""
import re
import shutil
from pathlib import Path


# любые обрамляющие "украшения" вокруг имени файла
_DECOR = "`*#_\\s>·•-"

# имя файла: что-то/path/имя.py (с точкой, слэшами, дефисами, подчёркиваниями)
_FNAME_RE = re.compile(r'^[' + re.escape(_DECOR) + r']*'
                       r'([A-Za-z0-9_./\-]+\.py)'
                       r'[' + re.escape(_DECOR) + r']*$')


def _looks_like_filename(line: str):
    """Вернуть имя .py-файла, если строка похожа на заголовок. Иначе None."""
    s = line.strip()
    if not s or len(s) > 120:
        return None
    # отсекаем строки, которые явно код
    if s.startswith(("import ", "from ", "def ", "class ", "if ", "for ", "while ", "return ")):
        return None
    m = _FNAME_RE.match(s)
    if not m:
        return None
    name = m.group(1)
    # отсекаем явные пути, начинающиеся с / или содержащие ..
    if name.startswith("/") or ".." in name:
        return None
    return name


def extract_snippets(text: str):
    """Список (filename, code). Устойчиво к разной разметке."""
    lines = text.splitlines()
    out = []
    pending_name = None       # ближайший найденный заголовок
    in_code = False
    code_buf = []
    code_lang = None

    for raw in lines:
        line = raw.rstrip("\n")

        # --- начало или конец код-блока ---
        if line.lstrip().startswith("```"):
            fence = line.lstrip()
            if not in_code:
                # открытие
                in_code = True
                code_lang = fence[3:].strip().lower()
                code_buf = []
            else:
                # закрытие
                if code_lang in ("python", "py", ""):
                    if pending_name:
                        out.append((pending_name, "\n".join(code_buf)))
                        pending_name = None
                    else:
                        print("  [warn] python-блок без заголовка — пропуск")
                in_code = False
                code_lang = None
                code_buf = []
            continue

        if in_code:
            code_buf.append(line)
            continue

        # --- вне кода: ищем заголовок ---
        name = _looks_like_filename(line)
        if name:
            pending_name = name

    return out


def main():
    root = Path(__file__).resolve().parent
    written, backed_up, seen = 0, 0, set()

    for src_name in ("new1.py", "new2.py"):
        src = root / src_name
        if not src.exists():
            print(f"[SKIP] {src_name} не найден")
            continue

        text = src.read_text(encoding="utf-8", errors="replace")
        snippets = extract_snippets(text)
        print(f"[READ] {src_name}: найдено блоков — {len(snippets)}")

        if not snippets:
            # диагностика: покажем, что вообще есть в файле
            print("  диагностика первых 40 строк, где могут быть '###':")
            for i, ln in enumerate(text.splitlines()[:200]):
                if "`" in ln or ln.lstrip().startswith("#") or ".py" in ln:
                    print(f"    {i+1:>4}: {ln[:100]}")
            print("  ...конец диагностики")

        for fname, code in snippets:
            if fname in seen:
                print(f"  [dup]   {fname} — уже был, перезапишу")
            seen.add(fname)

            target = root / fname
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists() and target.read_text(encoding="utf-8").strip():
                bak = target.parent / (target.name + ".bak")
                shutil.copy2(target, bak)
                backed_up += 1
                print(f"  [bak]   {fname}  →  {bak.name}")

            target.write_text(code + "\n", encoding="utf-8")
            print(f"  [write] {fname}  ({len(code)} симв.)")
            written += 1

    print()
    print(f"Готово. Записано файлов: {written}, бэкапов: {backed_up}")
    print(f"Корень: {root}")


if __name__ == "__main__":
    main()