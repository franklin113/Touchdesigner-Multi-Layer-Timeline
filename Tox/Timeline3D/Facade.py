"""This class is meant to facilitate the transfer of data between the time comp and the Playback comp
The time comp doesn't know anything about who/what will be receiving commands. All it knows is it's sending 
callbacks to this.
"""
class Facade:
	"""
	Facade description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.TimeComp = op('Time')
		self.Playback = op('Playback')
		self.CueTypes = dict()
		self.BuildCueTypes()	# this gets assigned in the TypeBuilder class on startup

	def BuildCueTypes(self):
		"""On startup we are generating a dictionary filled with cuetype callback classes.
		this is meant for speedy transfer of info. No reason to call getattr 3 times every single time
		a timer ends. We already have to do it once here.
		"""
		cueTypes = op('Cues/CueTypes').findChildren(type=COMP)
		for i in cueTypes:
			self.CueTypes[i.name] = getattr(getattr(op('Playback').mod, i.name), i.name)

	def DoCallback(self, callback:str , cueType: str, segment:int):
		"""The timer and other ops send this class triggers to perform a callback.
		Keep in mind that the time comp knows nothing about what you are doing with this. 
		All it is doing is transferring data. 

		For more information on the Facade design pattern, see Design Patterns book.

		Arguments:
			cueType {str} -- The name of the cue type that has just triggered something
			callback {str} -- The name of the trigger
			segment {int} -- The segment that just triggered this callback
		"""

		getattr(self.CueTypes[cueType], callback)(segment)	# by storing references to out types, we save a bit of speed.