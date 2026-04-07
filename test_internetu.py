import customtkinter as ctk
import speedtest
import threading
import numpy as np
import requests
from ping3 import ping
import time

# --- Funkcje ---

def get_isp():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5)
        data = r.json()
        org = data.get("org", "Nieznany operator")
        parts = org.split()
        if len(parts) > 1:
            return " ".join(parts[1:])
        return org
    except:
        return "Nieznany operator"

def measure_ping_jitter_loss(host, count=10):
    times = []
    lost = 0
    for _ in range(count):
        t = ping(host, timeout=1)
        if t is None:
            lost += 1
        else:
            times.append(t*1000)
    ping_avg = np.mean(times) if times else 0
    jitter = np.std(times) if len(times)>1 else 0
    packet_loss = (lost / count) * 100
    return ping_avg, jitter, packet_loss

def test_internetu():
    przycisk.configure(state="disabled")
    status_label.configure(text="Łączenie z serwerem...", text_color="orange")
    
    def run_test():
        try:
            isp = get_isp()
            isp_label.configure(text=f"Operator: {isp}")
            
            st = speedtest.Speedtest()
            best_server = st.get_best_server()
            
            status_label.configure(text="Test prędkości pobierania...", text_color="blue")
            download_speed = st.download() / 1_000_000
            color = "green" if download_speed>100 else "yellow" if download_speed>50 else "red"
            download_label.configure(text=f"Download: {download_speed:.2f} Mbps", text_color=color)
            
            status_label.configure(text="Test prędkości wysyłania...", text_color="blue")
            upload_speed = st.upload() / 1_000_000
            color = "green" if upload_speed>50 else "yellow" if upload_speed>20 else "red"
            upload_label.configure(text=f"Upload: {upload_speed:.2f} Mbps", text_color=color)
            
            status_label.configure(text="Pomiar Ping, Jitter i Packet Loss...", text_color="blue")
            host = best_server['host'].split(':')[0]
            ping_avg, jitter, packet_loss = measure_ping_jitter_loss(host, count=10)
            
            color = "green" if ping_avg<50 else "yellow" if ping_avg<100 else "red"
            ping_label.configure(text=f"Ping: {ping_avg:.1f} ms", text_color=color)
            
            color = "green" if jitter<10 else "yellow" if jitter<20 else "red"
            jitter_label.configure(text=f"Jitter: {jitter:.1f} ms", text_color=color)
            
            color = "green" if packet_loss<1 else "yellow" if packet_loss<3 else "red"
            packet_loss_label.configure(text=f"Packet Loss: {packet_loss:.1f} %", text_color=color)
            
            status_label.configure(text="Test zakończony!", text_color="green")
            
        except Exception as e:
            status_label.configure(text=f"Błąd: {e}", text_color="red")
        finally:
            przycisk.configure(state="normal")
    
    threading.Thread(target=run_test).start()

# --- GUI ---

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Test Internetu – Realne pomiary")
root.geometry("450x400")

status_label = ctk.CTkLabel(root, text="Kliknij przycisk, aby rozpocząć test", font=("Arial", 14))
status_label.pack(pady=10)

isp_label = ctk.CTkLabel(root, text="Operator: --", font=("Arial", 12))
isp_label.pack(pady=5)

download_label = ctk.CTkLabel(root, text="Download: -- Mbps", font=("Arial", 12))
download_label.pack(pady=5)

upload_label = ctk.CTkLabel(root, text="Upload: -- Mbps", font=("Arial", 12))
upload_label.pack(pady=5)

ping_label = ctk.CTkLabel(root, text="Ping: -- ms", font=("Arial", 12))
ping_label.pack(pady=5)

jitter_label = ctk.CTkLabel(root, text="Jitter: -- ms", font=("Arial", 12))
jitter_label.pack(pady=5)

packet_loss_label = ctk.CTkLabel(root, text="Packet Loss: -- %", font=("Arial", 12))
packet_loss_label.pack(pady=5)

przycisk = ctk.CTkButton(root, text="Rozpocznij test", command=test_internetu, width=200, height=40)
przycisk.pack(pady=20)

# --- PODPIS (LEWY DOLNY RÓG) ---
autor_label = ctk.CTkLabel(
    root,
    text="Autor: Mateusz Halka\nKontakt: lotnik9@o2.pl",
    font=("Arial", 10),
    justify="left"
)
autor_label.place(x=10, rely=1.0, anchor="sw")

root.mainloop()
