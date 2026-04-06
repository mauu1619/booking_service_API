from datetime import date

from taskiq_redis import ListQueueBroker
from pydantic import NameEmail
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings
from app.core.logger import logger

broker = ListQueueBroker(settings.redis_url)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM="test@example.com"
)

fm = FastMail(conf)


@broker.task
async def send_booking_email(name: str, email: str, date_from: date, date_to: date, total_cost: str):
    logger.info("Email task started", username=name)
    message = MessageSchema(
        subject="Your booking is confirmed!",
        recipients=[NameEmail(name=name, email=email)],
        body=f"""
            <h1>Remembering: </h1>
            <p>Date begin: '{date_from}'</p>
            <p>Date end: '{date_to}'</p>
            <p>Cost: {total_cost}</p>

            <i>Have a good days!</i>        
        """,
        subtype=MessageType.html
    )
    
    try:
        await fm.send_message(message)
    except Exception:
        logger.exception("Email sending failed")
    else:
        logger.info("Email sent", username=name, email=email)