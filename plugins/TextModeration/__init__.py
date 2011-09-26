from sbserver import *

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global textModerationHub
		textModerationHub = TextModerationHub()
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
Events = cxsbs.getResource("Events")

class TextModerationHub:
	def __init__(self):
		self.moderators = {}
		
	def register(self, t, f):
		if not t in self.moderators.keys():
			self.moderators[t] = []
			
		self.moderators[t].append(f)
		
	def moderate(self, t, cn, text):
		original = text
		if t in self.moderators.keys():
			for f in self.moderators[t]:
				temp = f(cn, text)
				if temp != None:
					text = temp
				else:
					#should log warning here regarding moderator returning None
					pass
		if text != original:
			Events.triggerServerEvent("text_moderated", (t, cn, original, text))
		return text

def registerTextModerator(t, f):
	textModerationHub.register(t, f)
	
def textModerate(t, cn, text):
	return textModerationHub.moderate(t, cn, text)
	

