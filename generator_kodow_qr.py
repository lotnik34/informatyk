import customtkinter as ctk
from tkinter import filedialog, messagebox
import qrcode
from PIL import Image, ImageTk

class QRGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zaawansowany Generator Kodów QR")
        self.geometry("700x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.qr_image = None
        self.logo_path = None

        self.create_widgets()

    def create_widgets(self):
        # Tytuł
        ctk.CTkLabel(self, text="📱 Generator Kodów QR", font=("Arial", 24, "bold")).pack(pady=15)

        # Pole tekstowe z placeholderem
        self.input_text = ctk.CTkTextbox(self, width=500, height=100)
        self.input_text.pack(pady=10)
        placeholder = "Wpisz tutaj tekst lub adres URL..."
        self.input_text.insert("0.0", placeholder)
        self.input_text.bind("<FocusIn>", lambda e: self.clear_placeholder(placeholder))
        self.input_text.bind("<FocusOut>", lambda e: self.restore_placeholder(placeholder))

        # Parametry QR
        frame_options = ctk.CTkFrame(self)
        frame_options.pack(pady=10)

        ctk.CTkLabel(frame_options, text="Rozmiar (px):").grid(row=0, column=0, padx=10, pady=5)
        self.size_entry = ctk.CTkEntry(frame_options, width=100)
        self.size_entry.insert(0, "10")
        self.size_entry.grid(row=0, column=1)

        ctk.CTkLabel(frame_options, text="Kolor przodu:").grid(row=0, column=2, padx=10)
        self.fg_color = ctk.CTkEntry(frame_options, width=100)
        self.fg_color.insert(0, "black")
        self.fg_color.grid(row=0, column=3)

        ctk.CTkLabel(frame_options, text="Kolor tła:").grid(row=0, column=4, padx=10)
        self.bg_color = ctk.CTkEntry(frame_options, width=100)
        self.bg_color.insert(0, "white")
        self.bg_color.grid(row=0, column=5)

        # Logo (opcjonalne)
        ctk.CTkButton(self, text="Wybierz logo (opcjonalne)", command=self.load_logo).pack(pady=5)

        # Przyciski
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Generuj QR", command=self.generate_qr).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Zapisz jako PNG", command=self.save_qr).grid(row=0, column=1, padx=10)

        # Podgląd QR
        self.qr_label = ctk.CTkLabel(self, text="")
        self.qr_label.pack(pady=10, expand=True)

        # Stopka – podpis autora
        footer = ctk.CTkLabel(
            self,
            text="Autor: Mateusz Halka   |   Kontakt: lotnik9@o2.pl",
            font=("Arial", 12),
            text_color="gray"
        )
        footer.pack(side="bottom", pady=10)

    def clear_placeholder(self, placeholder):
        if self.input_text.get("0.0", "end").strip() == placeholder:
            self.input_text.delete("0.0", "end")

    def restore_placeholder(self, placeholder):
        if not self.input_text.get("0.0", "end").strip():
            self.input_text.insert("0.0", placeholder)

    def load_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pliki graficzne", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.logo_path = file_path
            messagebox.showinfo("Logo", "Logo zostało załadowane pomyślnie!")

    def generate_qr(self):
        data = self.input_text.get("0.0", "end").strip()
        if not data or data == "Wpisz tutaj tekst lub adres URL...":
            messagebox.showerror("Błąd", "Pole tekstowe jest puste!")
            return

        try:
            size = int(self.size_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Rozmiar musi być liczbą całkowitą!")
            return

        fg_color = self.fg_color.get()
        bg_color = self.bg_color.get()

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        try:
            img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")
        except ValueError:
            messagebox.showerror("Błąd", "Niepoprawny kolor!")
            return

        # Dodanie logo
        if self.logo_path:
            logo = Image.open(self.logo_path).convert("RGBA")
            max_logo_size = int(min(img.size) * 0.25)
            logo.thumbnail((max_logo_size, max_logo_size), Image.LANCZOS)
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos, mask=logo)

        self.qr_image = img
        self.show_qr(img)

    def show_qr(self, img):
        # Dopasowanie podglądu QR
        img_resized = img.resize((250, 250))
        tk_img = ImageTk.PhotoImage(img_resized)
        self.qr_label.configure(image=tk_img)
        self.qr_label.image = tk_img

    def save_qr(self):
        if not self.qr_image:
            messagebox.showerror("Błąd", "Najpierw wygeneruj kod QR!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Pliki PNG", "*.png")])
        if file_path:
            self.qr_image.save(file_path)
            messagebox.showinfo("Zapisano", f"Plik zapisano jako: {file_path}")


if __name__ == "__main__":
    app = QRGeneratorApp()
    app.mainloop()

