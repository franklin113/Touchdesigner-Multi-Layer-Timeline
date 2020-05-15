# me - this DAT.
# timerOp - the connected Timer CHOP
# cycle - the cycle index
# segment - the segment index
# fraction - the time in fractional form
#
# interrupt - True if the user initiated a premature
# interrupt, False if a result of a normal timeout.
#
# onInitialize(): if return value > 0, it will be
# called again after the returned number of frames.
mainComp = parent.Main
null_Segments = op('null_Segments')
def onInitialize(timerOp):
	return 0

def onReady(timerOp):
	return
	
def onStart(timerOp):
	return
	
def onTimerPulse(timerOp, segment):
	# cueType = op('null_Segments')[segment,'Cuetype'].val
	# mainComp.DoCallback('TimerPulse', cueType, segment)
	return

def whileTimerActive(timerOp, segment, cycle, fraction):
	return

def onSegmentEnter(timerOp, segment, interrupt):
	
	print('segment: ', interrupt)
	if null_Segments.numRows > 1:
		cueType = null_Segments[segment+1,'Cuetype'].val
		if cueType != '':
			mainComp.DoCallback('Start', cueType, segment)
	return
	
def onSegmentExit(timerOp, segment, interrupt):
	if null_Segments.numRows > 1:
		cueType = null_Segments[segment+1,'Cuetype'].val
		if cueType != '':
			mainComp.DoCallback('End', cueType, segment)
	return

def onCycleStart(timerOp, segment, cycle):
	if null_Segments.numRows > 1:
		cueType = null_Segments[segment+1,'Cuetype'].val
		if cueType != '':
			mainComp.DoCallback('CycleStart', cueType, segment)
	return

def onCycleEndAlert(timerOp, segment, cycle, alertSegment, alertDone, interrupt):
	if null_Segments.numRows > 1:
		cueType = null_Segments[segment+1,'Cuetype'].val
		if cueType != '':
			mainComp.DoCallback('CycleEndAlert', cueType, segment)
	return
	
def onCycle(timerOp, segment, cycle):
	if null_Segments.numRows > 1:
		cueType = null_Segments[segment+1,'Cuetype'].val
		if cueType != '':
			mainComp.DoCallback('Cycle', cueType, segment)
	return

def onDone(timerOp, segment, interrupt):
	return
	