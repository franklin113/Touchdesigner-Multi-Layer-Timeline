# me - this DAT
# scriptOp - the OP which is cooking

renderPickComp = parent.Main.op('RenderPick')
timeConst = op('constant_ProposedStartTime')

prevOffset = 0
prevStartTime = 0
# press 'Setup Parameters' in the OP to call this function to re-create the parameters.
def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('Custom')
	p = page.appendFloat('Threshold', label='Threshold')
	return

# called whenever custom pulse parameter is pushed
def onPulse(par):
	return

def onCook(scriptOp):
	global prevStartTime

	scriptOp.clear()
	proposedTime = scriptOp.inputs[4]['startTime'].eval() 		# the time given to us by the render pick ext
	proposedEndTime = scriptOp.inputs[4]['endTime'].eval()		# the assumed end time based on the length of the selected cues

	######  The previous and next cues compared to either the start of the cue or end of the cue ######
	prevNextOfStart = [scriptOp.inputs[0][0].vals[-1], scriptOp.inputs[1][0].vals[0]]
	prevNextOfEnd = [scriptOp.inputs[2][0].vals[-1], scriptOp.inputs[3][0].vals[0]]

	##### The closest cue to either the start or end of the cue ######
	closestValA = [prevNextOfStart[0],prevNextOfStart[1]][ abs(prevNextOfStart[1] - proposedTime) <= abs(prevNextOfStart[0] - proposedTime) ]
	closestValB = [prevNextOfEnd[0],prevNextOfEnd[1]][ abs(prevNextOfEnd[1] - proposedEndTime) <= abs(prevNextOfEnd[0] - proposedEndTime) ]

	THRESH = scriptOp.par.Threshold.eval()
	### Do comparisons  between cue start, cue end, and the upcoming snap points ### 
	thresholdTestA = min(abs(prevNextOfStart[0] - proposedTime) , abs(prevNextOfStart[1] - proposedTime)) < THRESH
	thresholdTestB = min(abs(prevNextOfEnd[0] - proposedEndTime) , abs(prevNextOfEnd[1] - proposedEndTime)) < THRESH

	timeOffset = 0	# the time that we will be offseting all our cues

	if thresholdTestA:
		timeOffset = proposedTime - closestValA
	
	elif thresholdTestB:
		timeOffset = proposedEndTime - closestValB

	c= scriptOp.appendChan('FinalTime')	# we aren't really using this, but it causes it to cook
	c[0] = timeOffset


	if prevStartTime != proposedTime: # Don't assing anything if it hasn't changed.
		renderPickComp.SetAllSelectionStartTimes(timeOffset = timeOffset)

	prevStartTime = proposedTime	# to fix a cooking issue, don't do anything if prev and proposed are the same.

	return
