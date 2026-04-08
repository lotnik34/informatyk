import customtkinter as ctk
import subprocess
import re
import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def znajdz_router():
    try:
        # Pobranie danych z ipconfig z poprawnym kodowaniem
        wynik = subprocess.check_output("ipconfig", encoding="cp1250", errors="ignore")
        
        # Szukanie IP routera (PL + EN system)
        dopasowanie = re.search(r"(Default Gateway|Brama domyślna).*: ([0-9.]+)", wynik)
        
        if dopasowanie:
            return dopasowanie.group(2)
        else:
            return "Nie znaleziono"
    except Exception as e:
        return "Błąd"

def polacz():
    ip = label_ip.cget("text")
    if ip not in ["Nie znaleziono", "Błąd"]:
        webbrowser.open(f"http://{ip}")

# OKNO
app = ctk.CTk()
app.title("Router Finder")
app.geometry("400x220")

# TYTUŁ
label_title = ctk.CTkLabel(app, text="Ip routera", font=("Arial", 20))
label_title.pack(pady=15)

# IP ROUTERA
ip_routera = znajdz_router()
label_ip = ctk.CTkLabel(app, text=ip_routera, font=("Arial", 18))
label_ip.pack(pady=10)

# PRZYCISK
button = ctk.CTkButton(app, text="Połącz z routerem", command=polacz)
button.pack(pady=20)


# STOPKA (lewy dolny róg - dynamicznie)
label_footer = ctk.CTkLabel(
    app,
    text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
    font=("Arial", 10),
    justify="left"
)
label_footer.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

app.mainloop()
