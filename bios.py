import customtkinter as ctk
import subprocess
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def run_ps(cmd):
    try:
        result = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", cmd],
            stderr=subprocess.DEVNULL,
            timeout=8
        )
        return result.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        return "Timeout"
    except:
        return "Brak danych"


# 🔐 Secure Boot
def get_secure_boot_info():
    data = {}

    firmware = run_ps("(Get-CimInstance Win32_ComputerSystem).BootupState")

    if "EFI" in firmware or "UEFI" in firmware:
        data["Tryb systemu"] = "UEFI"
    else:
        data["Tryb systemu"] = "Legacy BIOS"

    sb = run_ps("Confirm-SecureBootUEFI")

    if "True" in sb:
        data["Secure Boot"] = "Włączony ✅"
        data["Obsługiwany"] = "Tak"
        data["Można włączyć"] = "Już aktywny"
    elif "False" in sb:
        data["Secure Boot"] = "Wyłączony ⚠️"
        data["Obsługiwany"] = "Tak"
        data["Można włączyć"] = "Tak (BIOS)"
    else:
        data["Secure Boot"] = "Brak / nieobsługiwany ❌"
        data["Obsługiwany"] = "Nie"
        data["Można włączyć"] = "Nie (Legacy)"

    return data


# 💾 NVMe FULL INFO 🔥
def get_nvme_info():
    data = {}

    nvme_check = run_ps("Get-PhysicalDisk | Where-Object {$_.BusType -eq 'NVMe'}")

    if not nvme_check or nvme_check == "Brak danych":
        data["NVMe"] = "Brak ❌"
        return data

    data["NVMe"] = "Wykryto ✅"

    # model
    models = run_ps("(Get-PhysicalDisk | Where-Object {$_.BusType -eq 'NVMe'}).FriendlyName")
    data["Model NVMe"] = models if models else "Brak danych"

    # rozmiar
    sizes = run_ps("(Get-PhysicalDisk | Where-Object {$_.BusType -eq 'NVMe'} | Select-Object -ExpandProperty Size)")
    try:
        sizes_list = sizes.split("\n")
        sizes_gb = [str(round(int(s) / (1024**3), 2)) + " GB" for s in sizes_list if s.strip()]
        data["Rozmiar NVMe"] = ", ".join(sizes_gb)
    except:
        data["Rozmiar NVMe"] = "Nieznany"

    # 🌡️ temperatura
    temp = run_ps("""
    Get-PhysicalDisk | Where-Object {$_.BusType -eq 'NVMe'} |
    Get-StorageReliabilityCounter | Select-Object -ExpandProperty Temperature
    """)

    if temp and temp != "Brak danych":
        temps = [t + " °C" for t in temp.split("\n") if t.strip()]
        data["Temperatura NVMe"] = ", ".join(temps)
    else:
        data["Temperatura NVMe"] = "Brak danych"

    # ❤️ zużycie
    wear = run_ps("""
    Get-PhysicalDisk | Where-Object {$_.BusType -eq 'NVMe'} |
    Get-StorageReliabilityCounter | Select-Object -ExpandProperty Wear
    """)

    if wear and wear != "Brak danych":
        wear_vals = [w + " %" for w in wear.split("\n") if w.strip()]
        data["Zużycie NVMe"] = ", ".join(wear_vals)
    else:
        data["Zużycie NVMe"] = "Brak danych"

    # 🚀 prędkość odczytu
    try:
        speed = run_ps("winsat disk -seq -read -drive c")
        match = re.search(r"Read\s+:\s+([\d\.]+)\s+MB/s", speed)

        if match:
            data["Prędkość odczytu"] = match.group(1) + " MB/s"
        else:
            data["Prędkość odczytu"] = "Nieznana"
    except:
        data["Prędkość odczytu"] = "Błąd"

    # 🚀 prędkość zapisu
    try:
        speed_w = run_ps("winsat disk -seq -write -drive c")
        match_w = re.search(r"Write\s+:\s+([\d\.]+)\s+MB/s", speed_w)

        if match_w:
            data["Prędkość zapisu"] = match_w.group(1) + " MB/s"
        else:
            data["Prędkość zapisu"] = "Nieznana"
    except:
        data["Prędkość zapisu"] = "Błąd"

    return data


def get_info():
    data = {}

    # BIOS
    data["Wersja BIOS"] = run_ps("(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion")
    data["Producent BIOS"] = run_ps("(Get-CimInstance Win32_BIOS).Manufacturer")

    # płyta
    data["Model płyty"] = run_ps("(Get-CimInstance Win32_BaseBoard).Product")
    data["Producent płyty"] = run_ps("(Get-CimInstance Win32_BaseBoard).Manufacturer")

    # Secure Boot
    data.update(get_secure_boot_info())

    # TPM
    tpm = run_ps("Get-Tpm")

    if "TpmPresent" in tpm:
        data["TPM"] = "Obecny ✅" if "True" in tpm else "Brak ❌"
    else:
        data["TPM"] = "Brak danych"

    tpm_version = run_ps(
        "(Get-WmiObject -Namespace root\\CIMV2\\Security\\MicrosoftTpm -Class Win32_Tpm).SpecVersion"
    )
    data["Wersja TPM"] = tpm_version if tpm_version else "Brak"

    # NVMe
    data.update(get_nvme_info())

    return data


def show_info():
    textbox.delete("1.0", "end")
    textbox.insert("end", "Pobieranie danych...\n")

    app.update()

    info = get_info()

    text = ""
    for key, value in info.items():
        text += f"{key}:\n{value}\n\n"

    textbox.delete("1.0", "end")
    textbox.insert("end", text)


# GUI
app = ctk.CTk()
app.title("BIOS / UEFI / Secure Boot / TPM / NVMe PRO")
app.geometry("650x550")

label = ctk.CTkLabel(app, text="Kliknij aby sprawdzić")
label.pack(pady=10)

button = ctk.CTkButton(app, text="Sprawdź", command=show_info)
button.pack(pady=10)

textbox = ctk.CTkTextbox(app, width=600, height=360)
textbox.pack(pady=10)

footer = ctk.CTkLabel(
    app,
    text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
    anchor="w",
    justify="left"
)
footer.pack(side="bottom", anchor="w", padx=10, pady=5)

app.mainloop()
