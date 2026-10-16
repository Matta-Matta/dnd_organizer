"""Модели данных для DND Master Organizer."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
import uuid


@dataclass
class Character:
    """Персонаж (Герой игрока или NPC)."""
    name: str
    char_type: str  # "Герой" или "NPC"
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    hp_current: int = 10
    hp_max: int = 10
    ac: int = 10
    abilities: str = ""
    notes: str = ""
    initiative: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        return cls(**data)


@dataclass
class Note:
    """Сюжетная заметка / ключевой пункт."""
    title: str
    text: str = ""
    status: str = "актуально"  # "актуально" или "выполнено"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(**data)


@dataclass
class AppData:
    """Все данные приложения."""
    characters: List[Character] = field(default_factory=list)
    notes: List[Note] = field(default_factory=list)
    combat_ids: List[str] = field(default_factory=list)  # id персонажей в текущем бою

    def to_dict(self) -> dict:
        return {
            "characters": [c.to_dict() for c in self.characters],
            "notes": [n.to_dict() for n in self.notes],
            "combat_ids": self.combat_ids,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppData":
        characters = [Character.from_dict(c) for c in data.get("characters", [])]
        notes = [Note.from_dict(n) for n in data.get("notes", [])]
        combat_ids = data.get("combat_ids", [])
        return cls(characters=characters, notes=notes, combat_ids=combat_ids)