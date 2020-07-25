"""Utils function"""

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import os
import sys
import yaml


def email2kindle(email_file_path: str):
    """Send the file to kindle"""

    # Load config file
    with open(r"./config.yaml") as file:
        configs = yaml.full_load(file)

    # server of the sending mail
    smtpserver = configs["smtpserver"]
    # Account/password
    password = configs["password"]
    sender = configs["sender"]
    # Receiver (kindle)
    receiver = configs["receiver"]

    # subject
    subject = "book from push2kindle"

    # main text
    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["from"] = sender
    msg["to"] = receiver

    msg.attach(MIMEText("Send by telegram bot push2kindle.", "plain", "utf-8"))

    # attachment
    att = MIMEApplication(open(email_file_path, "rb").read())
    att["Content-Type"] = "application/octet-stream"

    email_file_name = email_file_path.split("/")[-1]
    att.add_header(
        "Content-Disposition", "attachment", filename=("gbk", "", email_file_name)
    )
    msg.attach(att)

    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()


def epub2mobi(file_path: str) -> str:
    """Convert epub into mobi"""

    file_name = file_path[0:-5]
    os.system("ebook-convert " + file_path + " " + file_name + ".mobi")
    print("ebook-convert " + file_path + " " + file_name + ".mobi")
    return file_name + ".mobi"
