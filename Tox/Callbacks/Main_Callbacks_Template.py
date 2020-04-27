#Call via .Callbacks.Example(value) from the owner component.


def OnRightClick(value):
	debug(value)
	return
	
def OnPlayStateChange(value):
	# 0: Stop, 1: Play, 2: Pause
	debug(value)
	return