import re
import customtkinter as ctk
import pyperclip
from pathlib import Path
from core.vault import list_entries, read_entry, write_entry, delete_entry


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, vault_dir: Path, key: bytes):
        super().__init__(parent)
        self.vault_dir = vault_dir
        self.key = key
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Password Manager", font=("Arial", 15, "bold")).pack(pady=(15, 5))

        self._list = ctk.CTkTextbox(self, width=460, height=160, state="disabled")
        self._list.pack(padx=20, pady=5)

        ctk.CTkLabel(self, text="Service").pack()
        self._svc = ctk.CTkEntry(self, width=460, placeholder_text="e.g. gmail")
        self._svc.pack(padx=20, pady=3)

        ctk.CTkLabel(self, text="Credentials  (email | password)").pack()
        self._cred = ctk.CTkEntry(self, width=460, placeholder_text="e.g. user@gmail.com | mypassword")
        self._cred.pack(padx=20, pady=3)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=8)
        for i, (txt, cmd) in enumerate([
            ("Add",    self._add),
            ("Reveal", self._reveal),
            ("Copy",   self._copy),
            ("Delete", self._delete),
        ]):
            ctk.CTkButton(row, text=txt, width=100, command=cmd).grid(row=0, column=i, padx=4)

        self._out = ctk.CTkLabel(self, text="", wraplength=460)
        self._out.pack(pady=5)

        self._refresh()

    def _refresh(self):
        entries = list_entries(self.vault_dir)
        self._list.configure(state="normal")
        self._list.delete("1.0", "end")
        self._list.insert("end", "\n".join(entries) if entries else "(no entries)")
        self._list.configure(state="disabled")

    def _svc_name(self):
        return self._svc.get().strip().lower()

    def _add(self):
        svc, cred = self._svc_name(), self._cred.get().strip()
        if not svc or not cred:
            self._out.configure(text="Fill in both fields.", text_color="red")
            return
        if re.search(r'[\\/:*?"<>|]', svc):
            self._out.configure(text="Service name contains illegal characters.", text_color="red")
            return
        if (self.vault_dir / f"{svc}.enc").exists():
            self._out.configure(text=f"'{svc}' already exists. Delete it first to overwrite.", text_color="orange")
            return
        write_entry(self.vault_dir, svc, cred, self.key)
        self._out.configure(text=f"Saved: {svc}", text_color="green")
        self._svc.delete(0, "end")
        self._cred.delete(0, "end")
        self._refresh()

    def _reveal(self):
        svc = self._svc_name()
        if not svc:
            self._out.configure(text="Enter a service name.", text_color="red")
            return
        try:
            self._out.configure(text=read_entry(self.vault_dir, svc, self.key), text_color="white")
        except Exception:
            self._out.configure(text="Not found.", text_color="red")

    def _copy(self):
        svc = self._svc_name()
        if not svc:
            self._out.configure(text="Enter a service name.", text_color="red")
            return
        try:
            data = read_entry(self.vault_dir, svc, self.key)
            parts = data.split("|")
            pyperclip.copy(parts[-1].strip() if len(parts) > 1 else data)
            self._out.configure(text="Password copied. Clears in 30s.", text_color="green")
            self.after(30000, lambda: pyperclip.copy(""))
        except Exception:
            self._out.configure(text="Not found.", text_color="red")

    def _delete(self):
        svc = self._svc_name()
        if not svc:
            self._out.configure(text="Enter a service name.", text_color="red")
            return
        dialog = ctk.CTkInputDialog(text=f"Type '{svc}' to confirm delete:", title="Confirm Delete")
        if dialog.get_input() != svc:
            self._out.configure(text="Delete cancelled.", text_color="orange")
            return
        delete_entry(self.vault_dir, svc)
        self._out.configure(text=f"Deleted: {svc}", text_color="orange")
        self._refresh()