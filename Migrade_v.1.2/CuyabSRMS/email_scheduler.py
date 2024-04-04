import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Configure logging
logging.basicConfig(filename='email_scheduler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email():
    sender_email = 'cuyab.migrade@gmail.com'
    receiver_email = 'cuyab.migrade@gmail.com'
    password = 'hgwuscditxlkyfvu'
    subject = 'Scheduled Email'
    message = 'this is me friedgulaman again'

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # SMTP server setup
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        logging.info('Email sent successfully.')
    except Exception as e:
        logging.error(f'Error sending email: {str(e)}')

# Call the send_email function to send the email immediately
send_email()
