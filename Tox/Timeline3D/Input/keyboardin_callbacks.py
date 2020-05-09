# me - This DAT
# 
# dat - The DAT that received the key event
# key - The name of the key attached to the event.
#		This tries to be consistent regardless of which language
#		the keyboard is set to. The values will be the english/ASCII
#		values that most closely match the key pressed.
#		This is what should be used for shortcuts instead of 'character'.
# character - The unicode character generated.
# alt - True if the alt modifier is pressed
# ctrl - True if the ctrl modifier is pressed
# shift - True if the shift modifier is pressed
# state - True if the event is a key press event
# time - The time when the event came in milliseconds
# cmd - True if the cmd modifier is pressed
userSettings = ipar.UserSettings
systemSettings = ipar.SystemSettings

manager = parent.Main.op('Project')

def onKey(dat, key, character, alt, lAlt, rAlt, ctrl, lCtrl, rCtrl, shift, lShift, rShift, state, time, cmd, lCmd, rCmd):
	
	if state == 1: # only trigger on release
		return

	if key == 'delete' or key == 'backspace':
		manager.RemoveCues()

	return

# shortcutName is the name of the shortcut

def onShortcut(dat, shortcutName, time):
	
	if shortcutName == 'ctrl.-': # zoom out
		curZoom = userSettings.Zoom.eval()
		userSettings.Zoom = max(1,curZoom - .1)
		print('adf')
	
	elif shortcutName == 'ctrl.=':
		curZoom = userSettings.Zoom.eval()
		userSettings.Zoom = min(2,curZoom + .1)

	elif shortcutName == 'ctrl.c':
		manager.CopyOperation()
	
	elif shortcutName == 'ctrl.v':
		manager.PasteOperation()
	# shortcut = shortcutName[0].upper() + shortcutName[1:].replace('.','')
	
	
	# if hasattr(parent().par, shortcut):
	# 	setattr(parent().par, shortcut, True)
	
	# else:
		
	# 	if shortcutName == 'ctrl.1':
	# 		options = ['Cue','Output']
	# 		if ipar.Stage.Pickfocus == 'Cue':
	# 			ipar.Stage.Pickfocus = 'Output'
	# 		else:
	# 			ipar.Stage.Pickfocus = 'Cue'
	# 	elif shortcutName == 'ctrl.d':
	# 		selectionList = StageSettings.Selectionlist.eval()
	# 		for i in selectionList:
	# 			i.parent.Item.parent().Additem(copyOp = i.parent.Item)
	
	# 	elif shortcutName == 'ctrl.n':
	# 		UserSettings.Snapping = not UserSettings.Snapping.eval()
	
	return
	