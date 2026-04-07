import customtkinter as ctk
import psutil
import datetime
import wmi

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def formatuj_czas(czas):
    dni = czas.days
    sekundy = czas.seconds

    godziny = sekundy // 3600
    minuty = (sekundy % 3600) // 60
    sek = sekundy % 60

    if dni > 0:
        laczne_godziny = dni * 24 + godziny
        return f"{laczne_godziny} godzin"
    elif godziny > 0:
        return f"{godziny} godzin"
    elif minuty > 0:
        return f"{minuty} minut"
    else:
        return f"{sek} sekund"

def pobierz_informacje():
    dane = {}

    # Czas od ostatniego uruchomienia
    czas_startu = psutil.boot_time()
    czas_pracy = datetime.datetime.now() - datetime.datetime.fromtimestamp(czas_startu)
    dane["Czas od ostatniego uruchomienia komputera"] = formatuj_czas(czas_pracy)

    # Godziny od pierwszego uruchomienia (instalacji Windows)
    try:
        c = wmi.WMI()
        system = c.Win32_OperatingSystem()[0]
        data_instalacji = datetime.datetime.strptime(
            system.InstallDate.split('.')[0],
            "%Y%m%d%H%M%S"
        )
        godziny = int((datetime.datetime.now() - data_instalacji).total_seconds() / 3600)
        dane["Liczba godzin od pierwszego uruchomienia systemu"] = f"{godziny} godzin"
    except:
        dane["Liczba godzin od pierwszego uruchomienia systemu"] = "Niedostępne"

    return dane

def odswiez():
    pole_tekstu.configure(state="normal")
    pole_tekstu.delete("1.0", "end")

    dane = pobierz_informacje()
    for klucz, wartosc in dane.items():
        pole_tekstu.insert("end", f"{klucz}:\n{wartosc}\n\n")

    pole_tekstu.configure(state="disabled")

# ===== GUI =====
app = ctk.CTk()
app.title("Czas pracy komputera")
app.geometry("470x330")

ramka = ctk.CTkFrame(app)
ramka.pack(fill="both", expand=True, padx=20, pady=20)

tytul = ctk.CTkLabel(
    ramka,
    text="Informacje o czasie pracy komputera",
    font=("Arial", 18)
)
tytul.pack(pady=10)

pole_tekstu = ctk.CTkTextbox(ramka, width=430, height=170)
pole_tekstu.pack(pady=10)
pole_tekstu.configure(state="disabled")

przycisk = ctk.CTkButton(
    ramka,
    text="Odśwież dane",
    command=odswiez
)
przycisk.pack(pady=5)

# Stopka – lewy dół
stopka = ctk.CTkLabel(
    app,
    text="Autor: Mateusz Halka\nKontakt: lotnik9@o2.pl",
    font=("Arial", 10),
    justify="left"
)
stopka.place(relx=0.02, rely=0.93, anchor="w")
dodanie programu monitorowania czasu pracy komputera

odswiez()
app.mainloop()
