"""
Generator haseł Wi‑Fi — GUI z użyciem CustomTkinter
Plik: wifi_password_generator.py
Wymagania: customtkinter
Instalacja: pip install customtkinter

Funkcje:
- wybór długości hasła (slider)
- przełączniki: małe, duże litery, cyfry, symbole
- opcja wykluczania podobnych znaków (lIO0O)
- generuj i kopiuj do schowka
- zapisz do pliku txt
- ocena siły hasła

Autor: Mateusz Halka
Kontakt: lotnik9@o2.pl
"""

import customtkinter as ctk
import secrets
import string
import tkinter.messagebox as mb
from tkinter import filedialog

# Ustawienia wyglądu
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

SIMILAR = set("l1I0OoqQ")

class WifiPasswordGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generator hasła Wi‑Fi")
        self.geometry("520x400")
        self.resizable(False, False)

        # Frame główny
        frm = ctk.CTkFrame(master=self, corner_radius=10)
        frm.pack(padx=16, pady=16, fill="both", expand=True)

        title = ctk.CTkLabel(master=frm, text="Generator hasła Wi‑Fi", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(6, 12))

        # Długość
        self.length_var = ctk.IntVar(value=16)
        lbl_len = ctk.CTkLabel(master=frm, text="Długość:")
        lbl_len.grid(row=1, column=0, sticky="w", padx=(8,4))
        self.slider = ctk.CTkSlider(master=frm, from_=8, to=64, number_of_steps=56, command=self.on_length_change)
        self.slider.set(16)
        self.slider.grid(row=1, column=1, sticky="ew", padx=8)
        self.len_display = ctk.CTkLabel(master=frm, text=str(self.length_var.get()))
        self.len_display.grid(row=1, column=2, sticky="e", padx=(4,8))

        # Opcje znaków
        self.lower_var = ctk.BooleanVar(value=True)
        self.upper_var = ctk.BooleanVar(value=True)
        self.digits_var = ctk.BooleanVar(value=True)
        self.symbols_var = ctk.BooleanVar(value=True)
        self.no_similar_var = ctk.BooleanVar(value=False)

        chk_lower = ctk.CTkCheckBox(master=frm, text="małe litery (a-z)", variable=self.lower_var)
        chk_upper = ctk.CTkCheckBox(master=frm, text="duże litery (A-Z)", variable=self.upper_var)
        chk_digits = ctk.CTkCheckBox(master=frm, text="cyfry (0-9)", variable=self.digits_var)
        chk_symbols = ctk.CTkCheckBox(master=frm, text="symbole (!@#...)", variable=self.symbols_var)
        chk_no_similar = ctk.CTkCheckBox(master=frm, text="wyklucz podobne znaki (l1I0O)", variable=self.no_similar_var)

        chk_lower.grid(row=2, column=0, sticky="w", padx=8, pady=(8,2))
        chk_upper.grid(row=2, column=1, sticky="w", padx=8, pady=(8,2))
        chk_digits.grid(row=2, column=2, sticky="w", padx=8, pady=(8,2))
        chk_symbols.grid(row=3, column=0, sticky="w", padx=8, pady=(2,8))
        chk_no_similar.grid(row=3, column=1, sticky="w", padx=8, pady=(2,8))

        # Output (hasło)
        self.pw_var = ctk.StringVar()
        entry = ctk.CTkEntry(master=frm, textvariable=self.pw_var, width=360, font=ctk.CTkFont(size=14))
        entry.grid(row=4, column=0, columnspan=2, padx=8, pady=(8,4), sticky="ew")

        btn_copy = ctk.CTkButton(master=frm, text="Kopiuj", command=self.copy_to_clipboard, width=80)
        btn_copy.grid(row=4, column=2, padx=8, pady=(8,4))

        # Przyciski generuj / zapisz
        btn_gen = ctk.CTkButton(master=frm, text="Generuj", command=self.generate_password, width=120)
        btn_gen.grid(row=5, column=0, pady=(8,12), padx=8, sticky="w")

        btn_save = ctk.CTkButton(master=frm, text="Zapisz do pliku...", command=self.save_to_file, width=140)
        btn_save.grid(row=5, column=1, pady=(8,12), padx=8, sticky="w")

        btn_quit = ctk.CTkButton(master=frm, text="Zamknij", command=self.destroy, width=100)
        btn_quit.grid(row=5, column=2, pady=(8,12), padx=8, sticky="e")

        # Siła hasła
        self.strength_lbl = ctk.CTkLabel(master=frm, text="Siła: -")
        self.strength_lbl.grid(row=6, column=0, columnspan=3, pady=(4,0))

        # Autor / kontakt
        self.footer_lbl = ctk.CTkLabel(master=frm, text="Autor: Mateusz Halka\nKontakt: lotnik9@o2.pl", anchor="w", justify="left", font=ctk.CTkFont(size=10, weight="normal"))
        self.footer_lbl.grid(row=7, column=0, columnspan=2, sticky="w", padx=8, pady=(12,4))

        # Kolumny rozciąganie
        frm.grid_columnconfigure(1, weight=1)

        # Generuj od razu jedno hasło
        self.generate_password()

    def on_length_change(self, value):
        val = int(float(value))
        self.length_var.set(val)
        self.len_display.configure(text=str(val))

    def build_charset(self):
        parts = []
        if self.lower_var.get():
            parts.append(string.ascii_lowercase)
        if self.upper_var.get():
            parts.append(string.ascii_uppercase)
        if self.digits_var.get():
            parts.append(string.digits)
        if self.symbols_var.get():
            parts.append('!@#$%&*?+-_=')

        if not parts:
            return ''

        charset = ''.join(parts)
        if self.no_similar_var.get():
            charset = ''.join(ch for ch in charset if ch not in SIMILAR)
        return charset

    def generate_password(self):
        length = self.length_var.get()
        charset = self.build_charset()
        if not charset:
            mb.showwarning("Brak znaków", "Wybierz przynajmniej jedną grupę znaków!")
            return

        pw = ''.join(secrets.choice(charset) for _ in range(length))
        pw = self._ensure_char_types(pw)

        self.pw_var.set(pw)
        self.strength_lbl.configure(text=f"Siła: {self.evaluate_strength(pw)}")

    def _ensure_char_types(self, pw):
        required = []
        if self.lower_var.get():
            required.append(string.ascii_lowercase)
        if self.upper_var.get():
            required.append(string.ascii_uppercase)
        if self.digits_var.get():
            required.append(string.digits)
        if self.symbols_var.get():
            required.append('!@#$%&*?+-_=')

        charset = self.build_charset()
        if not required or len(pw) < len(required):
            return pw

        pw_list = list(pw)
        for i, group in enumerate(required):
            if not any((c in group) for c in pw_list):
                idx = secrets.randbelow(len(pw_list))
                ch = secrets.choice([c for c in group if (not self.no_similar_var.get() or c not in SIMILAR)])
                pw_list[idx] = ch
        secrets.SystemRandom().shuffle(pw_list)
        return ''.join(pw_list)

    def evaluate_strength(self, pw: str) -> str:
        score = 0
        length = len(pw)
        types = 0
        if any(c.islower() for c in pw):
            types += 1
        if any(c.isupper() for c in pw):
            types += 1
        if any(c.isdigit() for c in pw):
            types += 1
        if any(c in '!@#$%&*?+-_=' for c in pw):
            types += 1

        if length >= 12 and types >= 3:
            score = 3
        elif length >= 10 and types >= 2:
            score = 2
        elif length >= 8:
            score = 1
        else:
            score = 0

        return {0: 'BARDZO SŁABE', 1: 'SŁABE', 2: 'DOBRE', 3: 'BARDZO DOBRE'}[score]

    def copy_to_clipboard(self):
        pw = self.pw_var.get()
        if not pw:
            return
        self.clipboard_clear()
        self.clipboard_append(pw)
        mb.showinfo("Skopiowano", "Hasło zostało skopiowane do schowka")

    def save_to_file(self):
        pw = self.pw_var.get()
        if not pw:
            mb.showwarning("Brak hasła", "Brak wygenerowanego hasła do zapisania")
            return
        fname = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Pliki tekstowe", "*.txt")], title="Zapisz hasło jako")
        if not fname:
            return
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(pw + '\n')
            mb.showinfo("Zapisano", f"Hasło zapisano w:\n{fname}")
        except Exception as e:
            mb.showerror("Błąd zapisu", str(e))


if __name__ == '__main__':
    app = WifiPasswordGenerator()
    app.mainloop()
