import customtkinter as ctk
import subprocess
import ctypes
import sys
import threading
import re
import os
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ===== ADMIN =====
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )

# ===== SLmgr =====
CREATE_NO_WINDOW = 0x08000000

def run_slmgr(args):
    system32 = os.path.join(os.environ["WINDIR"], "System32")
    cscript = os.path.join(system32, "cscript.exe")
    slmgr = os.path.join(system32, "slmgr.vbs")

    subprocess.run(
        [cscript, "//Nologo", slmgr] + args,
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW
    )

# ===== WALIDACJA =====
def is_valid_key(key):
    pattern = r"^[A-Z0-9]{5}(-[A-Z0-9]{5}){4}$"
    return re.match(pattern, key.upper()) is not None

# ===== FORMAT =====
def format_key(event):
    text = app.entry.get().upper()
    text = re.sub(r"[^A-Z0-9]", "", text)

    groups = [text[i:i+5] for i in range(0, len(text), 5)]
    formatted = "-".join(groups[:5])

    app.entry.delete(0, "end")
    app.entry.insert(0, formatted)

# ===== AKTYWACJA =====
def activate_windows(key):
    try:
        run_slmgr(["/ipk", key])
        time.sleep(2)

        run_slmgr(["/skms", "kms.digiboy.ir"])
        time.sleep(2)

        run_slmgr(["/ato"])
        time.sleep(3)

        return "✅ Aktywowano Windows"

    except Exception:
        return "❌ Błąd aktywacji"

# ===== GUI =====
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        global app
        app = self

        self.title("Aktywacja Windows")
        self.geometry("420x260")

        self.label = ctk.CTkLabel(
            self,
            text="Wpisz klucz produktu:",
            font=ctk.CTkFont(size=16)
        )
        self.label.pack(pady=20)

        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)

        self.entry.bind("<KeyRelease>", format_key)

        self.button = ctk.CTkButton(
            self,
            text="Aktywuj",
            command=self.start_activation
        )
        self.button.pack(pady=15)

        self.status = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status.pack(pady=10)

        self.footer = ctk.CTkLabel(
            self,
            text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
            font=ctk.CTkFont(size=11)
        )
        self.footer.place(relx=0.01, rely=0.99, anchor="sw")

    def start_activation(self):
        key = self.entry.get().strip().upper()

        if not key:
            self.status.configure(text="❌ Wpisz klucz")
            return

        if not is_valid_key(key):
            self.status.configure(text="❌ Niepoprawny format klucza")
            return

        self.button.configure(state="disabled")
        self.status.configure(text="⏳ Trwa aktywacja...")

        thread = threading.Thread(target=self.activate_thread, args=(key,))
        thread.start()

    def activate_thread(self, key):
        result = activate_windows(key)
        self.after(0, self.finish_activation, result)

    def finish_activation(self, result):
        self.status.configure(text=result)
        self.button.configure(state="normal")

# ===== START =====
if __name__ == "__main__":
    try:
        if not is_admin():
            restart_as_admin()
            sys.exit()

        app = App()
        app.mainloop()

    except Exception:
        pass
