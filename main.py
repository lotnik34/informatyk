import os
import smtplib
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from email import encoders
from dotenv import load_dotenv
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
    file: UploadFile = None
):
    msg = MIMEMultipart()
    
    msg["From"] = formataddr((str(Header(f"Formularz - {name}", "utf-8")), SENDER_EMAIL))
    msg["To"] = RECEIVER_EMAIL
    msg["Reply-To"] = sender_contact_email
    msg["Subject"] = Header(f"Formularz kontaktowy: {name}", "utf-8")
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="o2.pl")
    msg["X-Mailer"] = "FastAPI-SMTP-Client"

    body = (
        f"Wpłynęła nowa wiadomość ze strony internetowej:\n\n"
        f"Imię i nazwisko: {name}\n"
        f"E-mail klienta: {sender_contact_email}\n\n"
        f"Treść wiadomości:\n{message_text}\n"
    )

    msg.attach(MIMEText(body, "plain", "utf-8"))

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
async def home(request: Request, sent: bool = False, name: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "offers": OFFERS,
            "message_sent": sent,
            "sender_name": name,
        },
    )


@app.post("/kontakt")
async def contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    attachment: UploadFile = File(None),
):
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)