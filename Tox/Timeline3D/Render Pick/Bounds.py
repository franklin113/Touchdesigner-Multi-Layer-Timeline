from operator import attrgetter
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
from collections import namedtuple
class Bounds:
	"""
	Bounds description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.NextPoint = None
		self.PrevPoint = None
		self.MainComp = parent.Main
		self.User = ipar.UserSettings

		self.TimePosition = self.MainComp.op('select_CurrentTime')['timer_fraction_WorldPos']
		self.Playhead = op('/Multi_Layer_Timeline/Timeline3D/Canvas/geo_Playhead')
		self.SnappingDistance = 1	# this is set in the render pick extension
		self.Bounds = namedtuple('CueBounds', ['targetOp','xMin','xMax','yMin','yMax','yCenter'])
		self.Manager = parent.Main.op('Project')
		self.SnapPointObj = namedtuple('SnapPointObj', ['targetOp','type','val'])
		self.BoundsList = []
		self.SnapPoints = []
		self.UpdateAllBounds()
		self.SelectionBounds = []

	def BuildBoundsObj(self, targetOp, tx,ty, endTime):
		cueHeight = self.User.Cueheight.eval()
		xMin = tx
		xMax = endTime
		
		yMin = ty - cueHeight * .5
		yMax = ty + cueHeight * .5
		boundsObj = self.Bounds(targetOp = targetOp, xMin=xMin, yMin=yMin, xMax=xMax, yMax= yMax, yCenter=ty)

		return boundsObj

	def UpdateAllBounds(self):
		cues = self.Manager.GetOps(cue = True)
		self.BoundsList =  []
		self.SnapPoints = []
		for i in cues:
			tx = i.par.Tx.eval()
			ty = i.par.Ty.eval()
			endTime = i.par.Computedendtime.eval()
			bounds = self.BuildBoundsObj(i,tx,ty,endTime)
			self.BoundsList.append(bounds) # append a tuple, the op and the bounds object
			front = self.SnapPointObj(i,'front',tx)
			back = self.SnapPointObj(i, 'back', endTime)
			self.SnapPoints.extend([front,back])

		# add the playhead to the bounds list
		timePos = self.TimePosition.eval()

		timeSnapPoint = self.SnapPointObj(self.Playhead,'front',timePos)

		playheadBounds = self.BuildBoundsObj(self.Playhead, timePos,0,0)

		self.SnapPoints.append(timeSnapPoint)
		self.BoundsList.append(playheadBounds)
		
		self.BoundsList.sort(key=lambda x: x.xMin)
		self.SnapPoints.sort(key=lambda x: x.val)
		for index, curBounds in enumerate(self.SnapPoints):
			if curBounds.type == 'front':
				curBounds.targetOp.par.Timeorderindex.val = index
			elif curBounds.type == 'back':
				curBounds.targetOp.par.Endtimeorderindex.val = index

	def PrintBounds(self, bounds, title = 'Bounds'):
		print('---------')
		print(title)
		for i in bounds:
			print(i[0].name, round(i[1][0],3))
		print('---------')
	
	def CompareNeighbors(self, proposedStartTime: float, mouseXPosCurrent: float, mouseXPosSnapStart: float ):

		return (False)

	def SnapTest(self, mouseXPosCurrent, mouseXPosSnapStart):
		# return a time offset
		# create comparison list

		pass

	def StoreBounds(self, singleEntry: tuple = None, swapEntryIndex=None, listToReplace: list = None):
		
		if singleEntry:
			if len(singleEntry) != 2:
				# print('INCORRECT ENTRY TO STORE BOUNDS')
				return 'INCORRECT ENTRY TO STORE BOUNDS'
			AllCueBounds = self.FetchBounds()
			if swapEntryIndex != None:
				AllCueBounds[swapEntryIndex]=singleEntry
			else:
				AllCueBounds.append(singleEntry)
		
		else:
			AllCueBounds = listToReplace
			for ind, i in enumerate(AllCueBounds):
				curOp = i[0]
				# curBounds = i[1]
				if curOp == None:
					AllCueBounds.pop(ind)
				else:
					curOp.par.Timeorderindex.val = AllCueBounds.index(i)

		
		if not any((AllCueBounds == [], AllCueBounds == None)):
			# print(AllCueBounds)
			# print('coming from storeBoudns- len(',len(AllCueBounds[0][1]))

			self.myOp.store('AllCueBounds', AllCueBounds)
			return True
		else:
			return False

	def SetSelectionBounds(self, selectionMin, selectionMax):
		self.SelectionBounds = [selectionMin, selectionMax]
		# print(self.SelectionBounds)
	
	def GetSelectionBounds(self):
		return self.SelectionBounds