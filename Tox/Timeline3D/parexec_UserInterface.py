# me - this DAT
# par - the Par object that has changed
# val - the current value
# prev - the previous value
# 
# Make sure the corresponding toggle is enabled in the Parameter Execute DAT.

# inner10AIcon = parent.Main.op('Canvas/geo_TimeIcons_Inner10')
# inner10BIcon = parent.Main.op('Canvas/geo_TimeIcons_Inner10_2')
# inner10BIcon = parent.Main.op('Canvas/geo_TimeIcons_Inner10_2')
# ThirtySecIconsA = parent.Main.op('Canvas/geo_TimeIcons_30_Sec_Markers')
# ThirtySecIconsB = parent.Main.op('Canvas/geo_TimeIcons_30_Sec_Markers1')
# MinuteIconA = parent.Main.op('geo_TimeIcons_Minute')
# MinuteIconB = parent.Main.op('geo_TimeIcons_Minute2')

patternSwitch = parent.Main.op('Canvas/base_Settings_Processing/base_GetPattern/switch1')

projectOp = op('Project')

import re
import datetime

def UpdateSecondsPar(par):

	groupPatterns = ['seconds', 'minutes seconds', 'hours minutes seconds']
	digits = re.search(r'^(([0-5]?[0-9])?:?([0-5]?[0-9])?:?([0-5]?[0-9]))$', par.eval())
	digitGroups = [int(i) for i in digits.group().split(':')]
	numDigitGroups = len(digitGroups)
	timePattern = groupPatterns[numDigitGroups-1].split()
	timeArgs = dict(zip(timePattern, digitGroups))
	timeDeltaObj = datetime.timedelta(**timeArgs)
	prettyTime = str(timeDeltaObj)
	ipar.UserSettings.Timelinetimecode = prettyTime
	if int(ipar.UserSettings.Timelinelength) != int(timeDeltaObj.seconds):
		run('ipar.UserSettings.Timelinelength = {}'.format(timeDeltaObj.seconds), delayFrames=1)

def UpdateTimecodePar(par):
	parSeconds =  int(par)
	prettyTime = str(datetime.timedelta(seconds=parSeconds))
	ipar.UserSettings.Timelinetimecode = prettyTime


def onValueChange(par, prev,val):
	# use par.eval() to get current value
	parOwner = par.owner
	print(par.name)
	if par.name == 'Camerafollowsplayhead':
		pass

	elif par.name == 'Timelinetimecode':
		UpdateSecondsPar(par)

	elif par.name == 'Timelinelength':
		patternSwitch.par.index = GetZoomPattern(par.eval())
		renderOp = op('Render')
		renderOp.op('iparCamera').par.Lrange.val = 0
		renderOp.op('iparCamera').par.Rrange.val = 1
		renderOp.op('iparCamera').par.Camypos.val = 0
		run("op('{}').Zoom(-1,0)".format(renderOp), delayFrames=60)
		# this fixes the issue of the parameter viewer not updating
		parent.Main.par.Parametercomp.eval().cook(force=True)
		UpdateTimecodePar(par)
		layerheight = op('Render').ScreenSpaceToWorldspace(x= 0, offset = (100,100) ).x
		op('base_ss2ws').par.Onehundredpixels.val = layerheight


	elif par.name == 'Newtimelinename':
		name = par.eval()
	
		if name in projectOp.TimelineNames:
			par.owner.par.Createtimeline.enable=False
		else:
			par.owner.par.Createtimeline.enable=True
	return

def onPulse(par):
	parOwner = par.owner
	if par.name == 'Save':
		save = op('Project').ext.Saver.SaveToDisk()
		if save:
			print('Project Saved')
		else:
			print('Project was not saved')
	
	elif par.name == 'Loadproject':
		
		response = False
		if ipar.UserSettings.Activeproject.eval() != '':
			response = ui.messageBox('Close Project', 'Do you want to save before closing?',buttons=['Yes', 'No'])
			response = not response
		if ipar.UserSettings.File != '':
			projectOp.LoadProject(saveBeforeExit=response)
		else:
			return

	elif par.name == 'Closeproject':
		response = ui.messageBox('Close Project', 'Do you want to save before closing?',buttons=['Yes', 'No'])
		
		response = not response

		projectOp.CloseProject(saveBeforeExit=response)

	elif par.name == 'Addcue':
		parent.Main.op('Project').AddDefault(op('select_CurrentTime')['timer_fraction_WorldPos'].eval())

	elif par.name == 'Createtimeline':
		projectOp.AddTimeline(par.owner.par.Newtimelinename.eval())
		par.owner.par.Newtimelinename.val = ''
		par.enable = False

	elif par.name == 'Loadtimeline':
		projectOp.LoadTimeline(par.owner.par.Availabletimelines.eval())

	elif par.name == 'Deletetimeline':
		projectOp.DeleteTimeline(par.owner.par.Availabletimelines.eval())



	return




def onExpressionChange(par, val, prev):
	return

def onExportChange(par, val, prev):
	return

def onEnableChange(par, val, prev):
	return

def onModeChange(par, val, prev):
	return
	

def GetZoomPattern(timelineLength):
	pattern = 0

	# man, really not worth cleaning this up...
	
	if all((timelineLength >= 2, timelineLength < 13)): 	# ~ 10 sec
		pattern = 0

	elif all((timelineLength >= 13, timelineLength < 28)): # ~ 15 sec
		pattern = 1

	elif all((timelineLength >= 28, timelineLength < 50)): # ~ 30 sec
		pattern = 2

	elif all((timelineLength >= 50, timelineLength < 200)): # ~ 1 minute
		pattern = 3
	
	elif all((timelineLength >= 200, timelineLength < 500)): # ~ 5 minutes
		pattern = 4
	
	elif all((timelineLength >= 500, timelineLength < 800)): # ~ 10 minutes
		pattern = 5
	
	elif all((timelineLength >= 800, timelineLength < 1100)): # ~ 15 minutes
		pattern = 6
	
	elif all((timelineLength >= 1100, timelineLength < 1700)): # ~ 20 minutes
		pattern = 7

	elif all((timelineLength >= 1700, timelineLength < 2500)): # ~ 30 minutes
		pattern = 8

	elif all((timelineLength >= 2500, timelineLength < 3400)): # ~ 45 minutes
		pattern = 9

	elif all((timelineLength >= 3400, timelineLength < 5400)): # ~ 60 min
		pattern = 10
	
	elif all((timelineLength >= 5400, timelineLength < 6200)): # ~ 90 min
		pattern = 11

	elif all((timelineLength >= 6200, timelineLength < 10600)): # ~ 120 min
		pattern = 12
	
	elif all((timelineLength >= 10600, timelineLength < 21400)): # ~ 180 min
		pattern = 13

	elif all((timelineLength >= 21400, timelineLength < 71100)): # ~ 360 min +
		pattern = 14
	
	elif timelineLength >= 71100: # ~ 1200 min +
		pattern = 15
	#print(pattern)
	return pattern

	


