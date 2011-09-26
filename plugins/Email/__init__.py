import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass

import smtplib

from VerificationMessages import *

import cxsbs
Config = cxsbs.getResource("Config")

def send_email(receiver, subject, body, sender=None):
	if sender == None:
		sender = send_email_from
	msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" %(sender, receiver, subject, body))
	s = smtplib.SMTP('localhost')
	s.sendmail(sender, [receiver], msg)
	s.quit()
	
def isValidEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

def send_create_verification(email, serverName, initiatedTime, serverClusterName, verificationCode, administrativeEmail):
	pass

def init():
	global send_email_from, administrative_email
	config = Config.PluginConfig('email')
	send_email_from = config.getOption('Email', 'send_email_from', 'no.reply@mydomain.com')
	administrative_email = config.getOption('Email', 'administrative_email', 'admin@mydomain.com')
	
	global create_verification_subject, create_verification_body, change_verification_subject, change_verification_body, delete_verification_subject, delete_verification_body
	create_verification_subject = config.getOption('Email', 'create_verification_subject', create_verification_subject)
	create_verification_body = config.getOption('Email', 'create_verification_body', create_verification_body)
	
	change_verification_subject = config.getOption('Email', 'change_verification_subject', change_verification_subject)
	change_verification_body = config.getOption('Email', 'change_verification_body', change_verification_body)
	
	delete_verification_subject = config.getOption('Email', 'delete_verification_subject', delete_verification_subject)
	delete_verification_body = config.getOption('Email', 'delete_verification_body', delete_verification_body)
	
	del config