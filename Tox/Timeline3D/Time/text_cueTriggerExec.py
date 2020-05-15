# me - this DAT
# 
# channel - the Channel object which has changed
# sampleIndex - the index of the changed sample
# val - the numeric value of the changed sample
# prev - the previous sample value
# 
# Make sure the corresponding toggle is enabled in the CHOP Execute DAT.
mainOP = parent.Main
null_Segments = op('null_Segments')
def onOffToOn(channel, sampleIndex, val, prev):
	return

def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	"""
	When the cueTrigger chop value changes, we know that we have a new
	cue "block" needing to preload. A cue block is a group of cues that 
	are at the time time position. To Retrieve the cue block you need to check
	out the cueParser chop. Channel 2, "row", provides the row to retrieve data from the
	table.
	Here we are retrieving the row from cueParser and using that to find the cue type. 
	We send this up to the Callbacks Facade. (see one component up, "Facade")
	"""
	for i in op('cueParser')['row'].vals: # the "Cue Block"
		if i > 0:	# the first row is the beginning of the timeline. 
			continue
		cueType = null_Segments[int(i)+2,'Cuetype'].val	
		
		if cueType != '':
			mainOP.DoCallback('Preload', cueType, int(i))	# The Facade will pass this to the correct location


	return
	