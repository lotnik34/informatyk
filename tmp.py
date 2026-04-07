# ============================================================
#  AUTO ADMIN + TPM / SECURE BOOT / UEFI CHECKER (ROZSZERZONY)
#  Pokazuje:
#   - TPM: wersja (2.0 / 1.2 / BRAK / NIEZNANA)
#   - Możliwość zamontowania TPM: TAK / NIE
#   - Secure Boot
#   - Tryb uruchamiania UEFI / BIOS
# ============================================================

import ctypes, sys, os
import platform
import subprocess
import customtkinter as ctk
import json
import shutil
import traceback


# ------------------------------------------------------------
#  AUTO URUCHAMIANIE JAKO ADMINISTRATOR (Windows)
# ------------------------------------------------------------
def run_as_admin():
    if os.name != "nt":
        return
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        params = " ".join(['"%s"' % x for x in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        sys.exit()


run_as_admin()


# ------------------------------------------------------------
#  USTAWIENIA GUI
# ------------------------------------------------------------
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# ------------------------------------------------------------
#  FUNKCJA URUCHAMIAJĄCA KOMENDY W UKRYCIU
# ------------------------------------------------------------
def run_hidden(cmd, timeout=6):
    try:
        if os.name == "nt":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0

            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                startupinfo=si, creationflags=CREATE_NO_WINDOW,
                timeout=timeout
            )
        else:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return out.strip()

    except:
        return ""


# ============================================================
#  TPM – wersja
# ============================================================
def check_tpm_windows():
    try:
        # --- 1) PowerShell CIM ---
        raw = run_hidden([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance -Namespace root/CIMV2/Security/MicrosoftTpm -ClassName Win32_Tpm | ConvertTo-Json -Compress"
        ])

        if raw:
            idx = raw.find("{")
            if idx >= 0:
                raw = raw[idx:]

            try:
                data = json.loads(raw)
                if isinstance(data, list) and data:
                    data = data[0]

                present = str(data.get("TpmPresent", "")).lower()
                if present in ("true", "1"):
                    spec = data.get("SpecVersion") or ""

                    if "2." in spec:
                        return "2.0"
                    if "1." in spec:
                        return "1.2"

                    return "NIEZNANA"
            except:
                pass

        # --- 2) WMIC fallback ---
        raw = run_hidden([
            "wmic",
            "/namespace:\\\\root\\cimv2\\security\\microsofttpm",
            "path", "Win32_Tpm",
            "get", "/format:list"
        ])

        if not raw:
            raw = run_hidden(["wmic", "path", "Win32_Tpm", "get", "/format:list"])

        if raw:
            for line in raw.splitlines():
                line = line.strip().lower()
                if line.startswith("specversion="):
                    spec = line.split("=", 1)[1].strip()
                    if "2." in spec:
                        return "2.0"
                    if "1." in spec:
                        return "1.2"
                    return "NIEZNANA"

        # --- 3) Get-Tpm fallback ---
        raw = run_hidden([
            "powershell", "-NoProfile", "-Command",
            "(Get-Tpm).TpmPresent"
        ])
        if raw.lower().strip() in ("true", "1"):
            return "NIEZNANA"

        return "BRAK"

    except:
        return "BRAK"


def check_tpm_linux():
    if not (os.path.exists("/dev/tpm0") or os.path.exists("/dev/tpmrm0")):
        return "BRAK"

    tpm2 = shutil.which("tpm2_getcap")
    if tpm2:
        out = run_hidden([tpm2, "properties-fixed"])
        if "tpm2" in out.lower():
            return "2.0"

    return "NIEZNANA"


# ============================================================
#  TPM – czy można zamontować / włączyć
# ============================================================
def check_tpm_mountable_windows():
    try:
        raw = run_hidden([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance -Namespace root/CIMV2/Security/MicrosoftTpm -ClassName Win32_Tpm | ConvertTo-Json -Compress"
        ])

        if not raw:
            return "NIE"

        idx = raw.find("{")
        if idx >= 0:
            raw = raw[idx:]

        data = json.loads(raw)

        if isinstance(data, list) and data:
            data = data[0]

        present = str(data.get("TpmPresent", "")).lower()
        if present not in ("true", "1"):
            return "NIE (brak modułu)"

        enabled = str(data.get("IsEnabled_InitialValue", "")).lower()
        activated = str(data.get("IsActivated_InitialValue", "")).lower()

        # TPM wykryty, ale wyłączony → można zamontować
        if enabled in ("false", "0") or activated in ("false", "0"):
            return "TAK (można włączyć w UEFI)"

        return "TAK (aktywne)"

    except:
        return "NIE"


def check_tpm_mountable_linux():
    if not (os.path.exists("/dev/tpm0") or os.path.exists("/dev/tpmrm0")):
        return "NIE (brak urządzenia)"

    return "TAK (urządzenie dostępne)"


# ============================================================
#  Secure Boot
# ============================================================
def check_secure_boot_windows():
    raw = run_hidden(["powershell", "-NoProfile", "-Command", "Confirm-SecureBootUEFI"])
    if raw == "True":
        return "TAK"
    if raw == "False":
        return "NIE"
    return "NIEOBSŁUGIWANE"


def check_secure_boot_linux():
    path = "/sys/firmware/efi/vars/"
    if not os.path.exists(path):
        return "NIEOBSŁUGIWANE"

    for f in os.listdir(path):
        if f.lower().startswith("secureboot-"):
            try:
                val = open(os.path.join(path, f, "data"), "rb").read()
                return "TAK" if val == b"\x01" else "NIE"
            except:
                pass

    return "NIEOBSŁUGIWANE"


# ============================================================
#  UEFI / BIOS
# ============================================================
def get_fw_type_windows():
    try:
        ft = ctypes.c_uint()
        if ctypes.windll.kernel32.GetFirmwareType(ctypes.byref(ft)):
            if ft.value == 2:
                return "UEFI"
            if ft.value == 1:
                return "Legacy (BIOS)"
    except:
        pass
    return "NIEOBSŁUGIWANE"


def get_fw_type_linux():
    return "UEFI" if os.path.exists("/sys/firmware/efi") else "Legacy (BIOS)"


# ============================================================
#  GUI
# ============================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TPM / Secure Boot / UEFI Checker")
        self.geometry("700x500")

        ctk.CTkLabel(
            self, text="Sprawdzanie TPM, Secure Boot i UEFI",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=12)

        ctk.CTkButton(self, text="SPRAWDŹ TERAZ", command=self.run_check)\
            .pack(pady=10)

        self.l_tpm = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18))
        self.l_tpm.pack(pady=10)

        self.l_tpm_mount = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.l_tpm_mount.pack(pady=10)

        self.l_sb = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.l_sb.pack(pady=10)

        self.l_fw = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.l_fw.pack(pady=10)

        ctk.CTkLabel(
            self,
            text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
            font=ctk.CTkFont(size=11)
        ).pack(side="bottom", pady=10)

    def run_check(self):
        self.l_tpm.configure(text="Sprawdzam TPM...")
        self.l_tpm_mount.configure(text="Sprawdzam możliwość montażu TPM...")
        self.l_sb.configure(text="Sprawdzam Secure Boot...")
        self.l_fw.configure(text="Sprawdzam tryb uruchamiania...")

        self.update()

        if platform.system() == "Windows":
            tpm = check_tpm_windows()
            tpm_mount = check_tpm_mountable_windows()
            sb = check_secure_boot_windows()
            fw = get_fw_type_windows()
        else:
            tpm = check_tpm_linux()
            tpm_mount = check_tpm_mountable_linux()
            sb = check_secure_boot_linux()
            fw = get_fw_type_linux()

        self.l_tpm.configure(text=f"TPM: {tpm}")
        self.l_tpm_mount.configure(text=f"Można zamontować TPM: {tpm_mount}")
        self.l_sb.configure(text=f"Secure Boot: {sb}")
        self.l_fw.configure(text=f"Tryb uruchomienia: {fw}")


# ============================================================
#  MAIN
# ============================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()

