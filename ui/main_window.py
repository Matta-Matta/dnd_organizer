"""Главное окно приложения."""

import tkinter as tk
from tkinter import ttk, messagebox
from models import AppData
from storage import load_data, save_data
from ui.characters_tab import CharactersTab
from ui.initiative_tab import InitiativeTab
from ui.notes_tab import NotesTab


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DND Master Organizer")
        self.geometry("900x650")
        self.minsize(700, 550)

        self.data: AppData = load_data()

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Segoe UI", 12), padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", "#4a4a4a"), ("!selected", "#e0e0e0")],
                  foreground=[("selected", "white"), ("!selected", "black")])

        # Шрифт таблиц (меняй здесь размер)
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tab_characters = CharactersTab(self.notebook, self.data, self._on_data_changed)
        self.notebook.add(self.tab_characters, text="Персонажи")

        self.tab_initiative = InitiativeTab(self.notebook, self.data, self._on_data_changed)
        self.notebook.add(self.tab_initiative, text="Инициатива")

        self.tab_notes = NotesTab(self.notebook, self.data, self._on_data_changed)
        self.notebook.add(self.tab_notes, text="Заметки")

        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.status_label = ttk.Label(status_frame, text="Данные загружены. Этап 4 готов.")
        self.status_label.pack(side=tk.LEFT)

        ttk.Button(status_frame, text="Сохранить", command=self._save).pack(side=tk.RIGHT)

    def _on_data_changed(self):
        save_data(self.data)
        self.status_label.config(text="Изменения сохранены.")
        self.after(2000, lambda: self.status_label.config(text="Готово."))
        if hasattr(self, "tab_initiative"):
            self.tab_initiative.refresh()

    def _save(self):
        save_data(self.data)
        self.status_label.config(text="Данные сохранены.")
        self.after(2000, lambda: self.status_label.config(text="Готово."))

    def _on_close(self):
        save_data(self.data)
        self.destroy()