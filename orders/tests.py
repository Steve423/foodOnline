from email.mime.multipart import MIMEMultipart
from django.test import TestCase
import smtplib
import ssl
from decouple import config
from django.conf import settings
from django.core.mail import EmailMessage, message

#this temp email below came from  https://www.emailondeck.com/ 
rec_email="jorie72@qjactives.com"
sender_email = "aa@gmail.com"
print("__A__Test_send_email")
settings.configure()
host = settings.EMAIL_HOST
port = settings.EMAIL_PORT
username = settings.EMAIL_HOST_USER 
password = settings.EMAIL_HOST_PASSWORD 
use_tls = settings.EMAIL_USE_TLS 
timeout = settings.EMAIL_TIMEOUT 
password ='abc' #  get from env file
message = MIMEMultipart('related')
message = "This sent using Python"
print("__A_port_=_" + str(port))
mail_subject="a_test"
try:

    print("__A_email_host_user_=_" + str(username))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    status_code, response = server.ehlo()
    print(f"[*] Echoing the server: {status_code} {response}")

    status_code, response = server.starttls()
    print(f"[*] Starting tls connection: {status_code} {response}")
    print("__B_pass_=_" + str(password))
    print("___C_user_=_" + str(rec_email))
    status_code, response = server.login(sender_email,password)
    print(f"[*] Logging in: {status_code} {response}")

    # server.sendmail( rec_email, sender_email, message)
    server.sendmail( sender_email, rec_email,  message)
    print("__A_Past_sendmail")
    server.quit()
except Exception as e:
    print("_a_Error_", e)

