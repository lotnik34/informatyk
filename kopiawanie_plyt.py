import customtkinter as ctk
import psutil
import ctypes
import os
import shutil
import threading
import time
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def pobierz_nazwe_dysku(drive):

    name = ctypes.create_unicode_buffer(1024)

    ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive),
        name,
        ctypes.sizeof(name),
        None,
        None,
        None,
        None,
        0,
    )

    return name.value


def rozmiar_folderu(path):

    total = 0

    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass

    return total


class KopiujISO(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Kopiowanie płyty ISO")
        self.geometry("720x520")

        self.naped = ""
        self.folder = ""
        self.stop = False

        title = ctk.CTkLabel(self, text="Kopiowanie płyty ISO", font=("Segoe UI", 26))
        title.pack(pady=20)

        self.mapowanie = {}
        napedy = self.znajdz_napedy()

        self.lista = ctk.CTkOptionMenu(
            self,
            values=list(napedy.keys()),
            command=self.wybierz_naped,
            width=450
        )
        self.lista.pack(pady=10)

        self.mapowanie = napedy

        self.btn_folder = ctk.CTkButton(
            self,
            text="Wybierz folder docelowy",
            command=self.wybierz_folder
        )
        self.btn_folder.pack(pady=10)

        self.folder_label = ctk.CTkLabel(self, text="Folder docelowy: nie wybrano")
        self.folder_label.pack()

        self.progress = ctk.CTkProgressBar(self, width=450)
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.label_procent = ctk.CTkLabel(self, text="0 %")
        self.label_procent.pack()

        self.label_predkosc = ctk.CTkLabel(self, text="Prędkość: 0 MB/s")
        self.label_predkosc.pack()

        self.label_eta = ctk.CTkLabel(self, text="Pozostały czas: --")
        self.label_eta.pack()

        self.status = ctk.CTkLabel(self, text="")
        self.status.pack(pady=10)

        frame = ctk.CTkFrame(self)
        frame.pack(pady=20)

        start_btn = ctk.CTkButton(
            frame,
            text="Rozpocznij kopiowanie",
            command=self.start
        )
        start_btn.grid(row=0, column=0, padx=10)

        cancel_btn = ctk.CTkButton(
            frame,
            text="Anuluj",
            fg_color="red",
            command=self.anuluj
        )
        cancel_btn.grid(row=0, column=1, padx=10)

        # -----------------------------
        # stopka autor
        # -----------------------------
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", anchor="w", padx=10, pady=10)

        autor = ctk.CTkLabel(
            footer,
            text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
            font=("Segoe UI", 12),
            justify="left"
        )
        autor.pack(anchor="w")

    def znajdz_napedy(self):

        napedy = {}

        for p in psutil.disk_partitions():

            if "cdrom" in p.opts or p.fstype == "CDFS":

                litera = p.device
                nazwa = pobierz_nazwe_dysku(litera)

                if not nazwa:
                    nazwa = "Płyta"

                size = rozmiar_folderu(litera)
                size_gb = round(size / (1024**3), 2)

                opis = f"{litera} — {nazwa} ({size_gb} GB)"

                napedy[opis] = litera

        if not napedy:
            napedy["Brak płyt"] = ""

        return napedy

    def wybierz_naped(self, wybor):

        self.naped = self.mapowanie.get(wybor, "")

        self.status.configure(text=f"Wybrano: {wybor}")

    def wybierz_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.folder = folder

            self.folder_label.configure(
                text=f"Folder docelowy:\n{folder}"
            )

    def start(self):

        if not self.naped:
            self.status.configure(text="❌ Nie wybrano płyty")
            return

        if not self.folder:
            self.status.configure(text="❌ Nie wybrano folderu")
            return

        self.stop = False

        threading.Thread(target=self.kopiuj).start()

    def anuluj(self):

        self.stop = True
        self.status.configure(text="Kopiowanie anulowane")

    def aktualizuj_gui(self, progress, percent, speed, eta, copied, total):

        self.progress.set(progress)
        self.label_procent.configure(text=f"{percent} %")
        self.label_predkosc.configure(text=f"Prędkość: {speed:.2f} MB/s")
        self.label_eta.configure(text=f"Pozostały czas: {eta}")
        self.status.configure(text=f"Kopiowanie {copied}/{total}")

    def zakoncz(self):

        messagebox.showinfo(
            "Kopiowanie zakończone",
            "Płyta ISO została skopiowana poprawnie."
        )

    def kopiuj(self):

        pliki = []

        for root, dirs, files in os.walk(self.naped):
            for f in files:
                pliki.append(os.path.join(root, f))

        total = len(pliki)
        copied = 0
        copied_bytes = 0

        start = time.time()

        for plik in pliki:

            if self.stop:
                return

            rel = os.path.relpath(plik, self.naped)
            dst = os.path.join(self.folder, rel)

            os.makedirs(os.path.dirname(dst), exist_ok=True)

            try:
                size = os.path.getsize(plik)
                shutil.copy2(plik, dst)
                copied_bytes += size
            except:
                pass

            copied += 1

            progress = copied / total
            percent = int(progress * 100)

            elapsed = time.time() - start
            speed = copied_bytes / elapsed / (1024*1024) if elapsed > 0 else 0

            remain = int((elapsed / copied) * (total - copied)) if copied else 0
            m = remain // 60
            s = remain % 60

            eta = f"{m}m {s}s"

            self.after(
                0,
                self.aktualizuj_gui,
                progress,
                percent,
                speed,
                eta,
                copied,
                total
            )

        self.after(0, self.zakoncz)


app = KopiujISO()
app.mainloop()
