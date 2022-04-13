from planner import mailConfig, mail
from planner.constants import SITE_NAME

from flask_mail import Message

def sendMessage(recipients, subject, body):
	msg = Message(
		subject = f"[{SITE_NAME}] - {subject}",
		sender = mailConfig.USER,
		recipients = recipients,
		body = body
	)
	mail.send(msg)
