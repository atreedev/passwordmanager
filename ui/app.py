import customtkinter as ctk
from ui.screens.login import LoginScreen
from ui.screens.dashboard import DashboardScreen

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("520x520")
        self.resizable(False, False)
        self._show_login()

    def _show_login(self):
        self._clear()
        LoginScreen(self, on_success=self._show_dashboard).pack(fill="both", expand=True)

    def _show_dashboard(self, vault_dir, key):
        self._clear()
        DashboardScreen(self, vault_dir=vault_dir, key=key).pack(fill="both", expand=True)

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()