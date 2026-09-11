import os
import json
import base64
import random
import urllib.request
import urllib.error
from typing import List
from dotenv import load_dotenv

from fastapi import FastAPI, Form, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Wczytanie zmiennych z pliku .env (przydatne przy uruchamianiu lokalnym)
load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pobieranie zmiennych środowiskowych z Rendera / .env
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "informatyk2488@gmail.com")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "informatyk2488@gmail.com")

OFFERS = [
    {
        "title": "Tworzenie Aplikacji Python i Android Studio",
        "description": "Projektowanie oraz tworzenie dedykowanych aplikacji desktopowych i mobilnych.",
        "icon": "code",
    },
    {
        "title": "Serwis i Wsparcie IT",
        "description": "Diagnostyka sprzętowa, usuwanie usterek, optymalizacja systemów i doradztwo technologiczne.",
        "icon": "wrench",
    },
]


def send_email_in_background(
    name: str, 
    sender_contact_email: str, 
    message_text: str, 
    file_data_list: list = None
):
    """
    Funkcja wysyła e-mail przy użyciu protokołu HTTP (SendGrid API),
    omijając blokady tradycyjnego portu SMTP na darmowym planie Render.
    """
    try:
        url = "https://api.sendgrid.com/v3/mail/send"
        
        # Przygotowanie załączników (jeśli zostały dodane w formularzu)
        attachments = []
        if file_data_list:
            for fname, fbytes in file_data_list:
                encoded_file = base64.b64encode(fbytes).decode('utf-8')
                attachments.append({
                    "content": encoded_file,
                    "filename": fname,
                    "type": "application/octet-stream",
                    "disposition": "attachment"
                })

        # Treść HTML wiadomości
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h2 style="color: #2563eb;">Nowa wiadomość z formularza kontaktowego</h2>
            <p><strong>Imię i nazwisko:</strong> {name}</p>
            <p><strong>E-mail klienta:</strong> <a href="mailto:{sender_contact_email}">{sender_contact_email}</a></p>
            <hr style="border: none; border-top: 1px solid #ccc; margin: 20px 0;">
            <p><strong>Treść wiadomości:</strong></p>
            <blockquote style="background: #f3f4f6; padding: 15px; border-left: 4px solid #2563eb; margin: 0;">
              {message_text.replace('\n', '<br>')}
            </blockquote>
          </body>
        </html>
        """

        # Konstrukcja obiektu JSON dla SendGrid
        payload = {
            "personalizations": [
                {
                    "to": [{"email": RECEIVER_EMAIL}],
                    "subject": f"Nowe zgłoszenie od: {name}"
                }
            ],
            "from": {"email": SENDER_EMAIL, "name": "Formularz Kontaktowy"},
            "reply_to": {"email": sender_contact_email, "name": name},
            "content": [
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }

        if attachments:
            payload["attachments"] = attachments

        # Wysyłka zapytania POST przez natywny urllib
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Authorization', f'Bearer {SENDGRID_API_KEY}')
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req) as response:
            if response.status in [200, 202]:
                print(">>> E-MAIL WYSŁANY POMYŚLNIE PRZEZ SENDGRID API! <<<")
            else:
                print(f">>> SENDGRID KOD STATUSU: {response.status} <<<")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f">>> BŁĄD HTTP SENDGRID: {e.code} - {error_body} <<<")
    except Exception as e:
        print(f">>> BŁĄD PODCZAS WYSYŁANIA WIADOMOŚCI: {e} <<<")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, sent: bool = False, error: str = "", name: str = ""):
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    captcha_expected = num1 + num2

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "offers": OFFERS,
            "message_sent": sent,
            "error": error,
            "sender_name": name,
            "captcha_num1": num1,
            "captcha_num2": num2,
            "captcha_expected": captcha_expected,
            "site_url": "https://informatyk.onrender.com/",
        },
    )


@app.post("/kontakt")
async def contact(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    captcha_answer: str = Form(...),
    captcha_expected: str = Form(...),
    attachment: List[UploadFile] = File(None),
):
    # Weryfikacja działania CAPTCHA
    if captcha_answer.strip() != captcha_expected.strip():
        return RedirectResponse(
            url=f"/?error=captcha#kontakt", 
            status_code=303
        )

    # Odczyt danych z załączonych plików
    file_data_list = []
    if attachment:
        for file in attachment:
            if file and file.filename:
                content = await file.read()
                file_data_list.append((file.filename, content))

    # Wysłanie wiadomości w tle
    background_tasks.add_task(
        send_email_in_background, 
        name, 
        email, 
        message, 
        file_data_list
    )

    return RedirectResponse(
        url=f"/?sent=true&name={name}#kontakt", 
        status_code=303
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=True)