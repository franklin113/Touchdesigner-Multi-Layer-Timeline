
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class Cues:
	"""
	Cues description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.CueReferences = [
			self.myOp.op('select1'),
			self.myOp.op('par3'),
			self.myOp.op('base_CacheBuilder/base_Get_Cache_2_InstanceID_Map/parameter1')
			]


	def CookCueReferences(self):
		for i in self.CueReferences:
			i.cook(force=True)