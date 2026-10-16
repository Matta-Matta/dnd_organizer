"""Вкладка Инициатива: порядок ходов в бою."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import Character


class InitiativeTab(ttk.Frame):
    """Вкладка управления инициативой и порядком ходов."""

    def __init__(self, parent, app_data, on_change_callback):
        super().__init__(parent)
        self.app_data = app_data
        self.on_change = on_change_callback
        self.current_turn_index = 0

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=8)

        ttk.Button(top, text="Добавить в бой", command=self._add_to_combat).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Убрать из боя", command=self._remove_from_combat).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Задать инициативу", command=self._set_initiative).pack(side=tk.LEFT, padx=4)
        ttk.Separator(top, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(top, text="◀ Предыдущий", command=self._prev_turn).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Следующий ▶", command=self._next_turn).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Сбросить ход", command=self._reset_turn).pack(side=tk.LEFT, padx=4)

        columns = ("order", "name", "type", "initiative", "hp")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("order", text="#")
        self.tree.heading("name", text="Имя")
        self.tree.heading("type", text="Тип")
        self.tree.heading("initiative", text="Инициатива")
        self.tree.heading("hp", text="HP")

        self.tree.column("order", width=40, minwidth=30, anchor="center")
        self.tree.column("name", width=180, minwidth=100)
        self.tree.column("type", width=70, minwidth=50, anchor="center")
        self.tree.column("initiative", width=90, minwidth=70, anchor="center")
        self.tree.column("hp", width=90, minwidth=70, anchor="center")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(0, 8))

        self.tree.tag_configure("current", background="#5a7a5a", foreground="white")
        self.tree.bind("<Double-1>", lambda e: self._set_initiative())

        self.hint = ttk.Label(self, text="Добавьте персонажей в бой → задайте инициативу → используйте «Следующий»",
                              font=("Segoe UI", 9))
        self.hint.pack(fill=tk.X, padx=8, pady=(0, 4))

    def _get_combat_characters(self) -> list[Character]:
        chars = [c for c in self.app_data.characters if c.id in self.app_data.combat_ids]
        return sorted(chars, key=lambda c: c.initiative, reverse=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        combat = self._get_combat_characters()

        if not combat:
            self.current_turn_index = 0
            return

        if self.current_turn_index >= len(combat):
            self.current_turn_index = 0

        for i, char in enumerate(combat):
            hp_str = f"{char.hp_current}/{char.hp_max}"
            tags = ("current",) if i == self.current_turn_index else ()
            self.tree.insert("", tk.END, iid=char.id,
                             values=(i + 1, char.name, char.char_type, char.initiative, hp_str),
                             tags=tags)

    def _get_selected_id(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _add_to_combat(self):
        available = [c for c in self.app_data.characters if c.id not in self.app_data.combat_ids]
        if not available:
            messagebox.showinfo("Инфо", "Все персонажи уже в бою или список пуст.\nСначала добавьте персонажей на вкладке «Персонажи».")
            return

        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Добавить в бой")
        win.geometry("320x360")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        ttk.Label(win, text="Выберите персонажей (можно несколько):").pack(pady=8)

        listbox = tk.Listbox(win, selectmode=tk.MULTIPLE, font=("Segoe UI", 11))
        listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        for c in available:
            listbox.insert(tk.END, f"{c.name} ({c.char_type})")

        def on_ok():
            selected_indices = listbox.curselection()
            for i in selected_indices:
                char = available[i]
                if char.id not in self.app_data.combat_ids:
                    self.app_data.combat_ids.append(char.id)
            self.refresh()
            self.on_change()
            win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Добавить", command=on_ok).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Отмена", command=win.destroy).pack(side=tk.LEFT, padx=6)

    def _remove_from_combat(self):
        char_id = self._get_selected_id()
        if not char_id:
            messagebox.showinfo("Подсказка", "Сначала выберите персонажа в таблице")
            return
        if char_id in self.app_data.combat_ids:
            self.app_data.combat_ids.remove(char_id)
            self.refresh()
            self.on_change()

    def _set_initiative(self):
        char_id = self._get_selected_id()
        if not char_id:
            messagebox.showinfo("Подсказка", "Сначала выберите персонажа")
            return

        char = next((c for c in self.app_data.characters if c.id == char_id), None)
        if not char:
            return

        value = simpledialog.askinteger(
            "Инициатива",
            f"Инициатива для «{char.name}»:",
            initialvalue=char.initiative,
            minvalue=-10,
            maxvalue=50,
            parent=self.winfo_toplevel()
        )
        if value is not None:
            char.initiative = value
            self.refresh()
            self.on_change()

    def _next_turn(self):
        combat = self._get_combat_characters()
        if not combat:
            return
        self.current_turn_index = (self.current_turn_index + 1) % len(combat)
        self.refresh()

    def _prev_turn(self):
        combat = self._get_combat_characters()
        if not combat:
            return
        self.current_turn_index = (self.current_turn_index - 1) % len(combat)
        self.refresh()

    def _reset_turn(self):
        self.current_turn_index = 0
        self.refresh()