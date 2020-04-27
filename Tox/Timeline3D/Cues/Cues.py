
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class Cues:
	"""
	Cues description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp
