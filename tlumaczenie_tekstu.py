import customtkinter as ctk
from deep_translator import GoogleTranslator

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tłumacz - Dowolny język")
        self.geometry("750x600")

        # Lista języków
        self.languages = {
            "Automatyczny": "auto",
            "Polski": "pl",
            "Angielski": "en",
            "Niemiecki": "de",
            "Francuski": "fr",
            "Hiszpański": "es",
            "Włoski": "it",
            "Ukraiński": "uk",
            "Rosyjski": "ru",
            "Czeski": "cs",
            "Chiński": "zh-CN",
            "Japoński": "ja"
        }

        # Etykieta wejścia
        self.label = ctk.CTkLabel(self, text="Wpisz tekst:", font=("Arial", 16))
        self.label.pack(pady=10)

        # Pole tekstowe wejściowe
        self.input_text = ctk.CTkTextbox(self, width=700, height=150)
        self.input_text.pack(pady=10)

        # Wybór języka źródłowego
        self.source_menu = ctk.CTkOptionMenu(self, values=list(self.languages.keys()))
        self.source_menu.pack(pady=5)
        self.source_menu.set("Automatyczny")

        # Wybór języka docelowego
        self.target_menu = ctk.CTkOptionMenu(self, values=list(self.languages.keys()))
        self.target_menu.pack(pady=5)
        self.target_menu.set("Polski")

        # Przycisk tłumaczenia
        self.translate_button = ctk.CTkButton(self, text="Tłumacz", command=self.translate_text)
        self.translate_button.pack(pady=15)

        # Wynik
        self.output_label = ctk.CTkLabel(self, text="Wynik:", font=("Arial", 16))
        self.output_label.pack(pady=10)

        self.output_text = ctk.CTkTextbox(self, width=700, height=150)
        self.output_text.pack(pady=10)

        # 🔹 Podpis autora (lewy dolny róg)
        self.author_label = ctk.CTkLabel(
            self,
            text="Autor: Mateusz Halka\nKontakt: lotnik9@o2.pl",
            font=("Arial", 12),
            justify="left"
        )
        self.author_label.place(x=10, y=570, anchor="sw")

    def translate_text(self):
        text = self.input_text.get("1.0", "end").strip()
        source_language = self.languages[self.source_menu.get()]
        target_language = self.languages[self.target_menu.get()]

        if text:
            try:
                if source_language == target_language:
                    translated = text
                else:
                    translated = GoogleTranslator(
                        source=source_language,
                        target=target_language
                    ).translate(text)

                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", translated)

            except Exception as e:
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", f"Błąd: {e}")

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
