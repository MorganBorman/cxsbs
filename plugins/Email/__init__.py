import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

import smtplib

from VerificationMessages import *

import cxsbs
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")

def send_email(receiver, subject, body, sender=None):
	if sender == None:
		sender = settings['send_email_from']
	msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" %(sender, receiver, subject, body))
	#print (sender, [receiver], msg)
	s = smtplib.SMTP('localhost')
	s.sendmail(sender, [receiver], msg)
	s.quit()
	
def isValidEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False

def send_templated_email(symbolicName, email, **kwargs):
	template_subject = emailTemplates[symbolicName + "_subject"]
	template_body = emailTemplates[symbolicName + "_body"]
	
	subject = template_subject.substitute(kwargs)
	body = template_body.substitute(kwargs)
	
	send_email(email, subject, body)

pluginCategory = 'Email'
		
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

for key, details in verificationMessages.items():
	SettingsManager.addSetting(Setting.TemplateSetting	(
															category=pluginCategory,
															subcategory="Email Templates", 
															symbolicName=key,
															displayName=details[0], 
															default=details[1],
															doc=details[2]
														))
	
emailTemplates = SettingsManager.getAccessor(pluginCategory, "Email Templates")