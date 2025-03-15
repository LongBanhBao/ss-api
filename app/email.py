from email.message import EmailMessage

import aiosmtplib

# from fastapi import BackgroundTasks, FastAPI
from app.config import get_settings

settings = get_settings()

# Đọc thông tin email từ biến môi trường
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT
EMAIL_USERNAME = settings.EMAIL_USERNAME
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_FROM = settings.EMAIL_FROM


async def send_email(to_email: str, subject: str, content: str):
    """Hàm gửi email qua SMTP"""
    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=EMAIL_HOST,
            port=EMAIL_PORT,
            username=EMAIL_USERNAME,
            password=EMAIL_PASSWORD,
            use_tls=False,  # Dùng STARTTLS (Port 587)
            start_tls=True,
        )
        return {"message": "Email sent successfully!"}
    except Exception as e:
        return {"error": str(e)}


# @app.post("/send-email/")
# async def send_email_api(to_email: str, subject: str, content: str):
#     """API gửi email trực tiếp qua SMTP"""
#     return await send_email(to_email, subject, content)


# @app.post("/send-email-background/")
# async def send_email_background(
#     background_tasks: BackgroundTasks, to_email: str, subject: str, content: str
# ):
#     """API gửi email chạy nền (không chặn API)"""
#     background_tasks.add_task(send_email, to_email, subject, content)
#     return {"message": "Email is being sent in the background!"}
