"""Сохранение и загрузка данных в JSON."""

import json
from pathlib import Path
from models import AppData

DATA_FILE = Path(__file__).parent / "data.json"


def load_data() -> AppData:
    """Загружает данные из JSON. Если файла нет — возвращает пустые данные."""
    if not DATA_FILE.exists():
        return AppData()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return AppData.from_dict(raw)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка чтения data.json: {e}. Создаю новые данные.")
        return AppData()


def save_data(data: AppData) -> None:
    """Сохраняет данные в JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)