import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Mailjet SMTP credentials
smtp_username = 'bb1167880dd50d14e05339f64668fced'
smtp_password = 'af34f628c27a9898ab41978c2cd55662'

# Email content
from_email = 'IIIinsight@outlook.com'   # must match your verified sender
to_email = 'alexsutcliffe44@gmail.com'
subject = 'Hello from Mailjet + Python!'
body = 'This is a test email sent through Mailjet using Python.'

# Build the email
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

try:
    # Connect to Mailjet SMTP server
    server = smtplib.SMTP('in-v3.mailjet.com', 587)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print('✅ Email sent successfully!')
except Exception as e:
    print(f'❌ Failed to send email: {e}')