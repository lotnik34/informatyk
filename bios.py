import customtkinter as ctk
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def run_ps(cmd):
    try:
        result = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", cmd],
            stderr=subprocess.DEVNULL,
            timeout=5  # 🔥 zabezpieczenie przed zawieszeniem
        )
        return result.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        return "Timeout"
    except:
        return "Brak danych"

# 🔐 Secure Boot (rozszerzone)
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

def get_info():
    data = {}

    # BIOS
    data["Wersja BIOS"] = run_ps("(Get-CimInstance Win32_BIOS).SMBIOSBIOSVersion")
    data["Producent BIOS"] = run_ps("(Get-CimInstance Win32_BIOS).Manufacturer")

    # Płyta główna
    data["Model płyty"] = run_ps("(Get-CimInstance Win32_BaseBoard).Product")
    data["Producent płyty"] = run_ps("(Get-CimInstance Win32_BaseBoard).Manufacturer")

    # Secure Boot
    data.update(get_secure_boot_info())

    # TPM
    tpm = run_ps("Get-Tpm")

    if "TpmPresent" in tpm:
        if "True" in tpm:
            data["TPM"] = "Obecny ✅"
        else:
            data["TPM"] = "Brak ❌"
    else:
        data["TPM"] = "Brak danych"

    # TPM wersja
    tpm_version = run_ps(
        "(Get-WmiObject -Namespace root\\CIMV2\\Security\\MicrosoftTpm -Class Win32_Tpm).SpecVersion"
    )
    data["Wersja TPM"] = tpm_version if tpm_version else "Brak"

    return data

def show_info():
    textbox.delete("1.0", "end")
    textbox.insert("end", "Pobieranie danych...\n")

    app.update()  # 🔥 odświeżenie GUI (ważne)

    info = get_info()

    text = ""
    for key, value in info.items():
        text += f"{key}:\n{value}\n\n"

    textbox.delete("1.0", "end")
    textbox.insert("end", text)

# GUI
app = ctk.CTk()
app.title("BIOS / UEFI / Secure Boot / TPM")
app.geometry("600x500")

label = ctk.CTkLabel(app, text="Kliknij aby sprawdzić")
label.pack(pady=10)

button = ctk.CTkButton(app, text="Sprawdź", command=show_info)
button.pack(pady=10)

textbox = ctk.CTkTextbox(app, width=550, height=320)
textbox.pack(pady=10)

# 🧾 STOPKA (lewy dół)
footer = ctk.CTkLabel(
    app,
    text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
    anchor="w",
    justify="left"
)
footer.pack(side="bottom", anchor="w", padx=10, pady=5)

app.mainloop()
