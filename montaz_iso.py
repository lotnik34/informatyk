import customtkinter as ctk
import subprocess
import time
import os
from tkinter import filedialog

import threading
import pystray
from PIL import Image, ImageDraw

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

mounted_isos = []
iso_frames = []

CREATE_NO_WINDOW = 0x08000000


def format_size(size):
    if size >= 1_000_000_000_000:
        return f"{round(size/1_000_000_000_000,2)} TB"
    elif size >= 1_000_000_000:
        return f"{round(size/1_000_000_000,2)} GB"
    else:
        return f"{round(size/1_000_000,2)} MB"


def refresh_list():

    for frame in iso_frames:
        frame.destroy()

    iso_frames.clear()

    if not mounted_isos:
        empty_label = ctk.CTkLabel(list_frame, text="Brak załadowanych płyt")
        empty_label.pack()
        iso_frames.append(empty_label)
        return

    for iso in mounted_isos:

        frame = ctk.CTkFrame(list_frame)
        frame.pack(fill="x", pady=5)

        name = os.path.basename(iso)
        size = os.path.getsize(iso)

        label = ctk.CTkLabel(
            frame,
            text=f"{name} ({format_size(size)})"
        )
        label.pack(side="left", padx=10)

        remove_button = ctk.CTkButton(
            frame,
            text="Wyjmij płytę",
            width=110,
            command=lambda i=iso: unmount_iso(i)
        )
        remove_button.pack(side="right", padx=10)

        iso_frames.append(frame)


def add_iso():

    if len(mounted_isos) >= 10:
        return

    path = filedialog.askopenfilename(filetypes=[("ISO files", "*.iso")])
    if not path:
        return

    mounted_isos.append(path)

    subprocess.run([
        "powershell",
        "-Command",
        f"Mount-DiskImage -ImagePath '{path}'"
    ], creationflags=CREATE_NO_WINDOW)

    time.sleep(2)

    cmd = f"(Get-DiskImage -ImagePath '{path}' | Get-Volume).DriveLetter"

    result = subprocess.check_output(
        ["powershell", "-Command", cmd],
        creationflags=CREATE_NO_WINDOW
    )

    drive = result.decode().strip()

    if drive:
        subprocess.run(
            ["explorer", f"{drive}:\\"],
            creationflags=CREATE_NO_WINDOW
        )

    refresh_list()


def unmount_iso(path):

    subprocess.run([
        "powershell",
        "-Command",
        f"Dismount-DiskImage -ImagePath '{path}'"
    ], creationflags=CREATE_NO_WINDOW)

    if path in mounted_isos:
        mounted_isos.remove(path)

    refresh_list()


def unmount_all():

    for iso in mounted_isos:

        subprocess.run([
            "powershell",
            "-Command",
            f"Dismount-DiskImage -ImagePath '{iso}'"
        ], creationflags=CREATE_NO_WINDOW)

    mounted_isos.clear()

    refresh_list()


app = ctk.CTk()
app.title("ISO Manager")
app.geometry("420x450")

title = ctk.CTkLabel(app, text="ISO Manager", font=("Arial", 22))
title.pack(pady=15)

add_button = ctk.CTkButton(app, text="Dodaj kolejne ISO", command=add_iso)
add_button.pack(pady=5)

unmount_button = ctk.CTkButton(app, text="Wyjmij wszystkie płyty", command=unmount_all)
unmount_button.pack(pady=5)

list_frame = ctk.CTkFrame(app)
list_frame.pack(fill="both", expand=True, padx=20, pady=15)


author_label = ctk.CTkLabel(
    app,
    text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
    justify="left",
    font=("Arial", 11)
)
author_label.pack(anchor="w", padx=10, pady=5)


def hide_window():
    app.withdraw()


def show_window(icon, item):
    app.after(0, app.deiconify)


def quit_app(icon, item):
    icon.stop()
    app.destroy()


def create_tray():

    image = Image.new("RGB", (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="white")

    menu = pystray.Menu(
        pystray.MenuItem("Otwórz ISO Manager", show_window),
        pystray.MenuItem("Wyjdź", quit_app)
    )

    icon = pystray.Icon("iso_manager", image, "ISO Manager", menu)
    icon.run()


app.protocol("WM_DELETE_WINDOW", hide_window)

tray_thread = threading.Thread(target=create_tray, daemon=True)
tray_thread.start()

refresh_list()

app.mainloop()
