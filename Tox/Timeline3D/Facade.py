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
		self.DebugToggle = self.Playback.par.Facadedebug

	def DoCallback(self, callback:str , cueType: str, segment:int):
		"""The timer and other ops send this class triggers to perform a callback.
		Keep in mind that the time comp knows nothing about what you are doing with this. 
		All it is doing is transferring data. 

		For more information on the Facade design pattern, see Design Patterns book.

		Each cue type has it's own class which derives from a base class with all basic methods
		laid out for the designer to override. 

		Arguments:
			cueType {str} -- The name of the cue type that has just triggered something
			callback {str} -- The name of the trigger
			segment {int} -- The segment that just triggered this callback
		"""

		# get the extension object first, then get the method callback
		
		if self.DebugToggle.eval():
			print('From Facade\'s DoCallback: \n',"Callback: ", callback, "Cue Type: ", cueType, "Segment: ", segment)

		try:
			getattr(getattr(op('Playback').ext, cueType), callback)(callback, cueType, segment)
		except Exception as e:
			print("Exception inside of the Facade- check callbacks: \n\n", e)