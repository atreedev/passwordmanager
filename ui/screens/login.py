import customtkinter as ctk
from core.auth import (
    init_db, is_first_launch,
    set_master_pin, verify_master_pin, set_salts, get_salts
)
from core.crypto import generate_salt, derive_key
from core.vault import write_sentinel, resolve_vault, VAULT, DECOY


class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        init_db()
        self._first = is_first_launch()
        self._step = 0
        self._show_step()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _show_step(self):
        self._clear()
        [self._step_master_pin, self._step_key][self._step]()

    def _layout(self, title):
        ctk.CTkLabel(self, text=title, font=("Arial", 14)).pack(pady=(50, 10))
        e = ctk.CTkEntry(self, width=260, show="*")
        e.pack(pady=5)
        e.focus()
        self._err = ctk.CTkLabel(self, text="", text_color="red")
        self._err.pack()
        return e

    def _btn(self, label, cmd):
        ctk.CTkButton(self, text=label, width=260, command=cmd).pack(pady=8)

    def _step_master_pin(self):
        label = "Set Master PIN" if self._first else "Enter Master PIN"
        self._e = self._layout(label)
        self._btn("Set PIN" if self._first else "Continue", self._check_master_pin)

    def _check_master_pin(self):
        pin = self._e.get()
        if self._first:
            if len(pin) < 4:
                self._err.configure(text="Minimum 4 characters")
                return
            set_master_pin(pin)
            self._step = 1
            self._show_step()
        else:
            if verify_master_pin(pin):
                self._step = 1
                self._show_step()
            else:
                self._err.configure(text="Incorrect PIN")

    def _step_key(self):
        if self._first:
            self._step_setup_keys()
        else:
            self._step_enter_key()

    def _step_setup_keys(self):
        ctk.CTkLabel(self, text="Set REAL decryption key", font=("Arial", 14)).pack(pady=(30, 5))
        self._real_e = ctk.CTkEntry(self, width=260, show="*")
        self._real_e.pack(pady=5)
        self._real_e.focus()
        ctk.CTkLabel(self, text="Set FAKE decryption key (duress)", font=("Arial", 14)).pack(pady=(15, 5))
        self._fake_e = ctk.CTkEntry(self, width=260, show="*")
        self._fake_e.pack(pady=5)
        self._err = ctk.CTkLabel(self, text="", text_color="red")
        self._err.pack()
        self._btn("Initialize Vault", self._do_setup_keys)

    def _do_setup_keys(self):
        real, fake = self._real_e.get(), self._fake_e.get()
        if len(real) < 4 or len(fake) < 4:
            self._err.configure(text="Both keys must be at least 4 characters")
            return
        if real == fake:
            self._err.configure(text="Real and fake keys must be different")
            return
        vault_salt, decoy_salt = generate_salt(), generate_salt()
        set_salts(vault_salt, decoy_salt)
        real_key = derive_key(real, vault_salt)
        write_sentinel(VAULT, real_key)
        write_sentinel(DECOY, derive_key(fake, decoy_salt))
        self.on_success(VAULT, real_key)

    def _step_enter_key(self):
        self._e = self._layout("Enter Decryption Key")
        self._btn("Unlock", self._check_key)

    def _check_key(self):
        vault_salt, decoy_salt = get_salts()
        vault_dir, key = resolve_vault(self._e.get(), vault_salt, decoy_salt)
        if vault_dir is None:
            self._err.configure(text="Incorrect key")
            return
        self.on_success(vault_dir, key)