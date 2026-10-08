# create_tree.py
"""
Создаёт дерево проекта Clone City рядом с собой.
Запусти:  python create_tree.py
Уже существующие файлы не трогает.
"""
import os
from pathlib import Path


TREE = {
    # корневые модули
    "main.py": "",
    "config.py": "",
    "data.py": "",
    "utils.py": "",
    "assets.py": "",
    "world.py": "",
    "state.py": "",

    # entities/
    "entities/__init__.py": "",
    "entities/player.py": "",
    "entities/vehicles.py": "",
    "entities/npcs.py": "",
    "entities/bosses.py": "",
    "entities/projectiles.py": "",

    # systems/
    "systems/__init__.py": "",
    "systems/input.py": "",
    "systems/player.py": "",
    "systems/traffic.py": "",
    "systems/police.py": "",
    "systems/combat.py": "",
    "systems/bosses.py": "",
    "systems/spawning.py": "",
    "systems/interactions.py": "",
    "systems/weather_time.py": "",
    "systems/effects.py": "",
    "systems/wanted.py": "",
    "systems/cheats.py": "",

    # render/
    "render/__init__.py": "",
    "render/camera.py": "",
    "render/sprites.py": "",
    "render/world.py": "",
    "render/entities.py": "",
    "render/effects.py": "",
    "render/hud.py": "",
    "render/overlays.py": "",

    # assets/ — папка под спрайты, оставляем пустой
    "assets/.gitkeep": "",
}


def main():
    root = Path(__file__).resolve().parent
    created, skipped = 0, 0

    for rel_path, content in TREE.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            print(f"  [skip] {rel_path}")
            skipped += 1
            continue

        target.write_text(content, encoding="utf-8")
        print(f"  [new]  {rel_path}")
        created += 1

    print()
    print(f"Готово. Создано: {created}, пропущено (уже было): {skipped}")
    print(f"Корень: {root}")


if __name__ == "__main__":
    main()