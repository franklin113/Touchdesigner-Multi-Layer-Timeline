"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class Cache:
	"""
	Cache description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.text3DA = op('tex3d_Labels')
		self.text3DB = op('tex3d_Thumbnail')
		self.switch = op('switch1')
		self.CuesTable = op('table_Cues')

	def EndReplaceAll(self):
		'''	
			once we have looped through our entire table, clean up
			switch needs to go back to the constant so it stops cooking
			turn off replace single toggle so it stops cooking
		'''
		
		self.switch.par.index =  1
		self.text3DA.par.replacesingle.val = False
		self.text3DB.par.replacesingle.val = False

	def WriteCache(self, index=None, replaceAll = False, clear = False):
		'''
			This is where we actually generate the cache
			index: int
			replaceAll: bool - if enabled, replaces the entire table. this can take a while
			clear: if enabled, will clear all data from cache

		'''
		
		if replaceAll:
			self.switch.par.index = 0

			self.text3DA.par.replacesingle.val = True
			self.text3DB.par.replacesingle.val = True
			run("op('{}').par.start.pulse()".format(op('timer1')),delayFrames=5)

			# run("op('{}').EndReplaceAll()".format(parent()),delayFrames = self.ownerComp.par.Arraysize.eval())
		if index != None:
			self.switch.par.index.val =  1
			op('constant_Index').par.value0 = index
			
			run("op('{}').par.replacesinglepulse.pulse()".format(self.text3DA),delayFrames = 1)
			run("op('{}').par.replacesinglepulse.pulse()".format(self.text3DB),delayFrames = 1)

		if clear:
			self.text3DA.par.resetpulse.pulse()
			self.text3DB.par.resetpulse.pulse()

	def AddItem(self, opObj, isMulti = False):
		'''
			we can use an op object here
			opObj: the op you just added.
			isMulti: bool designating whether it's multiple items or not.
			
			Considering we need to give this system some time to actually cache the images, we are delaying the call
			to WriteCache.

		'''
		if isMulti:
			for ind, i in enumerate(opObj):
				self.CuesTable[i.digits,0] = i.path
				run('parent().WriteCache(index = op("{}").digits)'.format(i),delayFrames = (ind+3)*10,fromOP = me)

		else:
			self.CuesTable[opObj.digits,0] = opObj.path
			self.WriteCache(index = opObj.digits)
		
		

	def DeleteItem(self, index: list, clear: bool =  False, isMulti = False):
		
		'''
			This is called mainly from the manager class
			
			index: if isMulti, a list, otherwise it can just be an int

			We can't use an op object here because it will be deleted by the time we use it.

			clear: bool

		'''
		assert type(index) == list or type(index) == int or type(index) == float, "Wrong data type passed to delete item"
		
		if isMulti:
			for ind, i in enumerate(index):
				self.CuesTable[i,0] = ''
				run('parent().WriteCache(index = {})'.format(i),delayFrames = (ind+1)*3,fromOP = me)
		else:
				
			self.CuesTable[index,0] = ''
			self.WriteCache(index, clear=clear)

		if clear:
			op('table_Cues').clear(keepSize=True)	

	