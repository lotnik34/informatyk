import customtkinter as ctk
from tkinter import filedialog
from pdf2docx import Converter
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PDFtoWordApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF → Word Converter")
        self.geometry("500x300")

        self.pdf_path = ""

        # Tytuł
        self.label = ctk.CTkLabel(self, text="Konwerter PDF do Word", font=("Arial", 20))
        self.label.pack(pady=20)

        # Przycisk wybierania pliku
        self.select_button = ctk.CTkButton(self, text="Wybierz PDF", command=self.select_file)
        self.select_button.pack(pady=10)

        # Label z nazwą pliku
        self.file_label = ctk.CTkLabel(self, text="Nie wybrano pliku")
        self.file_label.pack(pady=5)

        # Przycisk konwersji
        self.convert_button = ctk.CTkButton(self, text="Konwertuj", command=self.convert_file)
        self.convert_button.pack(pady=20)

        # Status
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=10)

        # 🔻 STOPKA (lewy dolny róg)
        self.footer = ctk.CTkLabel(
            self,
            text="autor: Mateusz Halka\nkontakt: lotnik9@o2.pl",
            font=("Arial", 10),
            justify="left"
        )
        self.footer.place(relx=0.01, rely=0.99, anchor="sw")

    def select_file(self):
        file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file:
            self.pdf_path = file
            self.file_label.configure(text=os.path.basename(file))

    def convert_file(self):
        if not self.pdf_path:
            self.status_label.configure(text="Najpierw wybierz plik!")
            return

        try:
            output_file = self.pdf_path.replace(".pdf", ".docx")

            self.status_label.configure(text="Konwertowanie...")

            cv = Converter(self.pdf_path)
            cv.convert(output_file, start=0, end=None)
            cv.close()

            self.status_label.configure(text=f"Gotowe!\nZapisano: {output_file}")

        except Exception as e:
            self.status_label.configure(text=f"Błąd: {str(e)}")


if __name__ == "__main__":
    app = PDFtoWordApp()
    app.mainloop()
