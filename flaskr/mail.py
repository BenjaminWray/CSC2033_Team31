import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
from dotenv import load_dotenv

from models.database import User

# load environment variables from .env file
load_dotenv()

# Mailjet SMTP credentials
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_SECRET')
from_email = 'IIIinsight@outlook.com'

def send_email(reciever_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = reciever_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Mailjet SMTP server
        server = smtplib.SMTP('in-v3.mailjet.com', 587)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, reciever_email, msg.as_string())
        server.quit()
        print('✅ Email sent successfully!')
    except Exception as e:
        print(f'❌ Failed to send email: {e}')


def reg_email(user):
    subject = "User registration"
    body = ("Thank you for Registering an account with III Insight.\nWe look forward to helping you improve your "
            "knowledge on Industry, Innovation, and Infrastructure.\nTo help you improve your knowledge and "
            "understanding we have flashcards and quizzes and we hope to see you on our leaderboard sometime "
            "soon.\nFrom the III Insight team.")

    send_email(user.email, subject, body)
