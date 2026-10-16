"""Вкладка Заметки: ключевые пункты сюжета."""

import tkinter as tk
from tkinter import ttk, messagebox
from models import Note


class NoteDialog(tk.Toplevel):
    """Окно добавления / редактирования заметки."""

    def __init__(self, parent, note: Note | None = None):
        super().__init__(parent)
        self.title("Редактирование заметки" if note else "Новая заметка")
        self.geometry("480x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result: Note | None = None
        self.note = note

        self._build_form()
        if note:
            self._fill_form(note)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_form(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Заголовок *").grid(row=0, column=0, sticky="w", pady=4)
        self.title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.title_var, width=40).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Статус").grid(row=1, column=0, sticky="w", pady=4)
        self.status_var = tk.StringVar(value="актуально")
        status_combo = ttk.Combobox(
            frame, textvariable=self.status_var,
            values=["актуально", "выполнено"], state="readonly", width=37
        )
        status_combo.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Текст").grid(row=2, column=0, sticky="nw", pady=4)
        self.text_widget = tk.Text(frame, height=12, width=40, wrap=tk.WORD, font=("Segoe UI", 10))
        self.text_widget.grid(row=2, column=1, sticky="nsew", pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=12)
        ttk.Button(btn_frame, text="Сохранить", command=self._on_save).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=6)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

    def _fill_form(self, note: Note):
        self.title_var.set(note.title)
        self.status_var.set(note.status)
        self.text_widget.insert("1.0", note.text)

    def _on_save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Ошибка", "Заголовок обязателен", parent=self)
            return

        data = {
            "title": title,
            "text": self.text_widget.get("1.0", "end-1c").strip(),
            "status": self.status_var.get(),
        }

        if self.note:
            data["id"] = self.note.id
            self.result = Note(**data)
        else:
            self.result = Note(**data)

        self.destroy()


class NotesTab(ttk.Frame):
    """Вкладка со списком сюжетных заметок."""

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
        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(btn_frame, text="Отметить выполненным", command=self._mark_done).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Вернуть в актуальные", command=self._mark_active).pack(side=tk.LEFT, padx=4)

        columns = ("title", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("status", text="Статус")

        self.tree.column("title", width=400, minwidth=150)
        self.tree.column("status", width=120, minwidth=80, anchor="center")

        self.tree.tag_configure("актуально", foreground="#1a5c1a")
        self.tree.tag_configure("выполнено", foreground="#888888")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=(0, 8))

        self.tree.bind("<Double-1>", lambda e: self._edit())

        preview_frame = ttk.LabelFrame(self, text="Текст заметки", padding=6)
        preview_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.preview = tk.Text(preview_frame, height=5, wrap=tk.WORD, font=("Segoe UI", 10), state="disabled")
        self.preview.pack(fill=tk.X)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        notes = sorted(self.app_data.notes, key=lambda n: (n.status != "актуально", n.title.lower()))
        for note in notes:
            self.tree.insert("", tk.END, iid=note.id,
                             values=(note.title, note.status),
                             tags=(note.status,))

    def _get_selected(self) -> Note | None:
        selection = self.tree.selection()
        if not selection:
            return None
        note_id = selection[0]
        for n in self.app_data.notes:
            if n.id == note_id:
                return n
        return None

    def _on_select(self, event=None):
        note = self._get_selected()
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        if note:
            self.preview.insert("1.0", note.text or "(пусто)")
        self.preview.config(state="disabled")

    def _add(self):
        dialog = NoteDialog(self.winfo_toplevel())
        self.wait_window(dialog)
        if dialog.result:
            self.app_data.notes.append(dialog.result)
            self.refresh()
            self.on_change()

    def _edit(self):
        note = self._get_selected()
        if not note:
            messagebox.showinfo("Подсказка", "Сначала выберите заметку")
            return
        dialog = NoteDialog(self.winfo_toplevel(), note=note)
        self.wait_window(dialog)
        if dialog.result:
            idx = next(i for i, n in enumerate(self.app_data.notes) if n.id == note.id)
            self.app_data.notes[idx] = dialog.result
            self.refresh()
            self.on_change()
            self._on_select()

    def _delete(self):
        note = self._get_selected()
        if not note:
            messagebox.showinfo("Подсказка", "Сначала выберите заметку")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить заметку «{note.title}»?"):
            self.app_data.notes = [n for n in self.app_data.notes if n.id != note.id]
            self.refresh()
            self.on_change()
            self.preview.config(state="normal")
            self.preview.delete("1.0", tk.END)
            self.preview.config(state="disabled")

    def _mark_done(self):
        note = self._get_selected()
        if not note:
            messagebox.showinfo("Подсказка", "Сначала выберите заметку")
            return
        note.status = "выполнено"
        self.refresh()
        self.on_change()

    def _mark_active(self):
        note = self._get_selected()
        if not note:
            messagebox.showinfo("Подсказка", "Сначала выберите заметку")
            return
        note.status = "актуально"
        self.refresh()
        self.on_change()