from pathlib import Path

from fastapi_mail.errors import ConnectionErrors
from pydantic import BaseModel, EmailStr
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail

from src.repositories import auth as auth

HOST = 'localhost'

class EmailSchema(BaseModel):
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME="gfour@meta.ua",
    MAIL_PASSWORD="Arcobaleno1",
    MAIL_FROM="gfour@meta.ua",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Example email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr,  host: str = HOST):
    try:
        token_verification = await auth.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="example_email.html")
    except ConnectionErrors as err:
        print(err)