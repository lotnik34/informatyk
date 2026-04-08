import customtkinter as ctk
import subprocess
import json

# wygląd
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def get_ram_type(smbios_type):
    """Mapowanie SMBIOS → DDR"""
    ram_types = {
        20: "DDR",
        21: "DDR2",
        24: "DDR3",
        26: "DDR4",
        34: "DDR5"
    }
    return ram_types.get(smbios_type, "Nieznany")


def get_ram_info():
    try:
        cmd = [
            "powershell",
            "-Command",
            "Get-CimInstance Win32_PhysicalMemory | "
            "Select-Object Manufacturer, PartNumber, Capacity, Speed, ConfiguredVoltage, SMBIOSMemoryType | "
            "ConvertTo-Json"
        ]

        output = subprocess.check_output(cmd).decode("utf-8", errors="ignore")
        data = json.loads(output)

        textbox.delete("1.0", "end")

        if isinstance(data, dict):
            data = [data]

        for i, ram in enumerate(data, start=1):
            capacity_gb = round(int(ram["Capacity"]) / (1024**3), 2)

            voltage = ram.get("ConfiguredVoltage")
            smbios = ram.get("SMBIOSMemoryType")

            # DDR typ
            ram_type = get_ram_type(smbios)

            # konwersja napięcia
            if voltage in [None, 0]:
                voltage_text = "Brak danych (BIOS / CPU-Z)"
            else:
                voltage_v = voltage / 1000
                voltage_text = f"{voltage_v:.2f} V"

            textbox.insert("end", f"🔹 RAM #{i}\n")
            textbox.insert("end", f"Typ: {ram_type}\n")
            textbox.insert("end", f"Producent: {ram['Manufacturer']}\n")
            textbox.insert("end", f"Model: {ram['PartNumber']}\n")
            textbox.insert("end", f"Pojemność: {capacity_gb} GB\n")
            textbox.insert("end", f"Prędkość: {ram['Speed']} MHz\n")
            textbox.insert("end", f"Napięcie: {voltage_text}\n")
            textbox.insert("end", "-" * 40 + "\n")

    except Exception as e:
        textbox.delete("1.0", "end")
        textbox.insert("end", f"Błąd:\n{e}")


# GUI
app = ctk.CTk()
app.title("Informacje o RAM")
app.geometry("650x420")

title = ctk.CTkLabel(app, text="Szczegóły pamięci RAM", font=("Arial", 22))
title.pack(pady=10)

button = ctk.CTkButton(app, text="Pobierz informacje", command=get_ram_info)
button.pack(pady=10)

textbox = ctk.CTkTextbox(app, width=600, height=260)
textbox.pack(pady=10)

# stopka
footer = ctk.CTkLabel(
    app,
    text="Autor: Mateusz Halka\nKontakt: lotnik9@o2.pl",
    font=("Arial", 10),
    justify="left"
)
footer.place(x=10, rely=1.0, anchor="sw")

app.mainloop()
