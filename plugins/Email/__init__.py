import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

import smtplib, re

from VerificationMessages import *

import cxsbs
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")

def send_email(receiver, subject, body, sender=None):
	if sender == None:
		sender = settings['send_email_from']
	msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" %(sender, receiver, subject, body))
	
	connectString = settings['smtp_host'] + ":" + str(settings['smtp_port'])
	
	server = smtplib.SMTP(connectString)
	if settings['smtp_use_tls']:
		server.starttls()  
	server.login(settings['smtp_username'],settings['smtp_password'])
	server.sendmail(sender, [receiver], msg)
	server.quit() 
	
def isValidEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

def send_templated_email(symbolicName, email, **kwargs):
	#print kwargs
	
	template_subject = emailTemplates[symbolicName + "_subject"]
	template_body = emailTemplates[symbolicName + "_body"]
	
	kwargs.update({'newline':"\n", 'administrativeEmail': settings['administrative_email']})
	
	subject = template_subject.substitute(kwargs)
	body = template_body.substitute(kwargs)
	
	send_email(email, subject, body)

pluginCategory = 'Email'
		
SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="smtp_username", 
												displayName="Smtp username", 
												default="mygmailUser",
												doc="Username to connect to smtp server with."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="smtp_password", 
												displayName="Smtp password", 
												default="mygmailPass",
												doc="Password to connect to smtp server with."
											))
		
SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="smtp_host", 
												displayName="Smtp host", 
												default="smtp.gmail.com",
												doc="Smtp server to send email through."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="smtp_port", 
												displayName="Smtp port", 
												default=587,
												doc="Smtp server port to send email through."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="smtp_use_tls", 
												displayName="Smtp use tls", 
												default=True,
												doc="Should we use tls to connect to the smtp server."
											))
		
SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="send_email_from", 
												displayName="Send email from", 
												default="no.reply@mydomain.com",
												doc="Default address to send messages with."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="administrative_email", 
												displayName="Administrative email", 
												default="admin@mydomain.com",
												doc="Address to have users send questions or concerns to."
											))

settings = SettingsManager.getAccessor(pluginCategory, "General")

for key, details in AccountMessages.items():
	SettingsManager.addSetting(Setting.TemplateSetting	(
															category=pluginCategory,
															subcategory="Email Templates", 
															symbolicName=key,
															displayName=details[0], 
															default=details[1],
															doc=details[2]
														))
	
emailTemplates = SettingsManager.getAccessor(pluginCategory, "Email Templates")