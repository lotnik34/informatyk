import os
import random
import smtplib
from typing import List
from dotenv import load_dotenv

from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from email import encoders

from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Wczytanie danych z pliku .env
load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pobieranie danych z ustawień środowiskowych
SMTP_SERVER = "poczta.o2.pl"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

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


async def send_email_with_attachment(
    name: str, 
    sender_contact_email: str, 
    message_text: str, 
    files: List[UploadFile] = None
):
    msg = MIMEMultipart("mixed")
    
    msg["From"] = formataddr((str(Header("Formularz Kontaktowy", "utf-8")), SENDER_EMAIL))
    msg["To"] = RECEIVER_EMAIL
    msg["Reply-To"] = formataddr((str(Header(name, "utf-8")), sender_contact_email))
    msg["Subject"] = Header(f"Nowe zgłoszenie od: {name}", "utf-8")
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="o2.pl")
    
    msg["X-Mailer"] = "Python-FastAPI-ContactForm"
    msg["Auto-Submitted"] = "auto-generated"

    msg_body = MIMEMultipart("alternative")

    text_content = (
        f"Wpłynęła nowa wiadomość ze strony https://informatyk.onrender.com/:\n\n"
        f"Imię i nazwisko: {name}\n"
        f"E-mail klienta: {sender_contact_email}\n\n"
        f"Treść wiadomości:\n{message_text}\n"
    )
    
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

    msg_body.attach(MIMEText(text_content, "plain", "utf-8"))
    msg_body.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(msg_body)

    if files:
        for file in files:
            if file and file.filename:
                file_content = await file.read()
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{file.filename}"',
                )
                msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, sent: bool = False, error: str = "", name: str = ""):
    # Generowanie losowego działania matematycznego dla CAPTCHA
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
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    captcha_answer: str = Form(...),
    captcha_expected: str = Form(...),
    attachment: List[UploadFile] = File(None),
):
    # Weryfikacja przepisanego wyniku CAPTCHA
    if captcha_answer.strip() != captcha_expected.strip():
        return RedirectResponse(
            url=f"/?error=captcha#kontakt", 
            status_code=303
        )

    try:
        await send_email_with_attachment(name, email, message, attachment)
        return RedirectResponse(
            url=f"/?sent=true&name={name}#kontakt", 
            status_code=303
        )
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")
        return RedirectResponse(url="/#kontakt", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=True)