"""Вкладка Персонажи: список, добавление, редактирование, удаление."""

import tkinter as tk
from tkinter import ttk, messagebox
from models import Character


class CharacterDialog(tk.Toplevel):
    """Окно добавления / редактирования персонажа."""

    def __init__(self, parent, character: Character | None = None):
        super().__init__(parent)
        self.title("Редактирование персонажа" if character else "Новый персонаж")
        self.geometry("420x620")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result: Character | None = None
        self.character = character

        self._build_form()
        if character:
            self._fill_form(character)

        # Центрируем относительно родителя
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        # Имя
        ttk.Label(frame, text="Имя *").grid(row=0, column=0, sticky="w", pady=3)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=32).grid(row=0, column=1, sticky="ew", pady=3)

        # Тип
        ttk.Label(frame, text="Тип").grid(row=1, column=0, sticky="w", pady=3)
        self.type_var = tk.StringVar(value="Герой")
        type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=["Герой", "NPC"], state="readonly", width=29)
        type_combo.grid(row=1, column=1, sticky="ew", pady=3)

        # Характеристики
        stats = [
            ("Сила", "str_var"),
            ("Ловкость", "dex_var"),
            ("Телосложение", "con_var"),
            ("Интеллект", "int_var"),
            ("Мудрость", "wis_var"),
            ("Харизма", "cha_var"),
        ]
        self.stat_vars = {}
        for i, (label, attr) in enumerate(stats):
            ttk.Label(frame, text=label).grid(row=2 + i, column=0, sticky="w", pady=3)
            var = tk.IntVar(value=10)
            self.stat_vars[attr] = var
            ttk.Spinbox(frame, from_=1, to=30, textvariable=var, width=10).grid(row=2 + i, column=1, sticky="w", pady=3)

        # HP
        ttk.Label(frame, text="HP текущие").grid(row=8, column=0, sticky="w", pady=3)
        self.hp_cur_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=0, to=999, textvariable=self.hp_cur_var, width=10).grid(row=8, column=1, sticky="w", pady=3)

        ttk.Label(frame, text="HP максимум").grid(row=9, column=0, sticky="w", pady=3)
        self.hp_max_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=999, textvariable=self.hp_max_var, width=10).grid(row=9, column=1, sticky="w", pady=3)

        # AC
        ttk.Label(frame, text="Класс брони (AC)").grid(row=10, column=0, sticky="w", pady=3)
        self.ac_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=0, to=30, textvariable=self.ac_var, width=10).grid(row=10, column=1, sticky="w", pady=3)

        # Способности
        ttk.Label(frame, text="Способности").grid(row=11, column=0, sticky="nw", pady=3)
        self.abilities_text = tk.Text(frame, height=4, width=32, wrap=tk.WORD)
        self.abilities_text.grid(row=11, column=1, sticky="ew", pady=3)

        # Заметки
        ttk.Label(frame, text="Заметки").grid(row=12, column=0, sticky="nw", pady=3)
        self.notes_text = tk.Text(frame, height=4, width=32, wrap=tk.WORD)
        self.notes_text.grid(row=12, column=1, sticky="ew", pady=3)

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=13, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Сохранить", command=self._on_save).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=6)

        frame.columnconfigure(1, weight=1)

    def _fill_form(self, c: Character):
        self.name_var.set(c.name)
        self.type_var.set(c.char_type)
        self.stat_vars["str_var"].set(c.strength)
        self.stat_vars["dex_var"].set(c.dexterity)
        self.stat_vars["con_var"].set(c.constitution)
        self.stat_vars["int_var"].set(c.intelligence)
        self.stat_vars["wis_var"].set(c.wisdom)
        self.stat_vars["cha_var"].set(c.charisma)
        self.hp_cur_var.set(c.hp_current)
        self.hp_max_var.set(c.hp_max)
        self.ac_var.set(c.ac)
        self.abilities_text.insert("1.0", c.abilities)
        self.notes_text.insert("1.0", c.notes)

    def _on_save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Имя обязательно", parent=self)
            return

        data = {
            "name": name,
            "char_type": self.type_var.get(),
            "strength": self.stat_vars["str_var"].get(),
            "dexterity": self.stat_vars["dex_var"].get(),
            "constitution": self.stat_vars["con_var"].get(),
            "intelligence": self.stat_vars["int_var"].get(),
            "wisdom": self.stat_vars["wis_var"].get(),
            "charisma": self.stat_vars["cha_var"].get(),
            "hp_current": self.hp_cur_var.get(),
            "hp_max": self.hp_max_var.get(),
            "ac": self.ac_var.get(),
            "abilities": self.abilities_text.get("1.0", "end-1c").strip(),
            "notes": self.notes_text.get("1.0", "end-1c").strip(),
        }

        if self.character:
            data["id"] = self.character.id
            data["initiative"] = self.character.initiative
            self.result = Character(**data)
        else:
            self.result = Character(**data)

        self.destroy()


class CharactersTab(ttk.Frame):
    """Вкладка со списком персонажей."""

    def __init__(self, parent, app_data, on_change_callback):
        super().__init__(parent)
        self.app_data = app_data
        self.on_change = on_change_callback

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=8, pady=8)

        ttk.Button(btn_frame, text="Добавить", command=self._add).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Редактировать", command=self._edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Удалить", command=self._delete).pack(side=tk.LEFT, padx=4)

        columns = ("name", "type", "hp", "ac")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Имя")
        self.tree.heading("type", text="Тип")
        self.tree.heading("hp", text="HP")
        self.tree.heading("ac", text="AC")

        self.tree.column("name", width=200, minwidth=120)
        self.tree.column("type", width=80, minwidth=60, anchor="center")
        self.tree.column("hp", width=100, minwidth=70, anchor="center")
        self.tree.column("ac", width=60, minwidth=40, anchor="center")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(0, 8))

        self.tree.bind("<Double-1>", lambda e: self._edit())

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for char in self.app_data.characters:
            hp_str = f"{char.hp_current}/{char.hp_max}"
            self.tree.insert("", tk.END, iid=char.id, values=(char.name, char.char_type, hp_str, char.ac))

    def _get_selected(self) -> Character | None:
        selection = self.tree.selection()
        if not selection:
            return None
        char_id = selection[0]
        for c in self.app_data.characters:
            if c.id == char_id:
                return c
        return None

    def _add(self):
        dialog = CharacterDialog(self.winfo_toplevel())
        self.wait_window(dialog)
        if dialog.result:
            self.app_data.characters.append(dialog.result)
            self.refresh()
            self.on_change()

    def _edit(self):
        char = self._get_selected()
        if not char:
            messagebox.showinfo("Подсказка", "Сначала выберите персонажа")
            return
        dialog = CharacterDialog(self.winfo_toplevel(), character=char)
        self.wait_window(dialog)
        if dialog.result:
            idx = next(i for i, c in enumerate(self.app_data.characters) if c.id == char.id)
            self.app_data.characters[idx] = dialog.result
            self.refresh()
            self.on_change()

    def _delete(self):
        char = self._get_selected()
        if not char:
            messagebox.showinfo("Подсказка", "Сначала выберите персонажа")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить «{char.name}»?"):
            self.app_data.characters = [c for c in self.app_data.characters if c.id != char.id]
            if char.id in self.app_data.combat_ids:
                self.app_data.combat_ids.remove(char.id)
            self.refresh()
            self.on_change()