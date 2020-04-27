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
from collections import namedtuple
from pprint import pprint
class Selection:
	"""
	Selection description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		self.StartMousePos = (0,0)	# 0-1 space, where you click the mouse
		self.EndMousePos = (0,0)	# 0-1 space - where you released the mouse

		self.Bounds = namedtuple('Bounds', ['xMin', 'xMax','yMin','yMax'])

		self.SelectionBounds = self.Bounds(0,0,0,0)

		self.ObjectPositions = {} # pathToOp : tdu.Position
		self.ObjectPositionsNormalized = {} # pathToOp : tdu.Position
		
		self.MainCam = parent.Main.op('Render/cam1')

		self.ws2vs = None
		
		self.Selection = []
		self.OldSelection = []

		#self.GetInstancePositions()	# 'instance number' : bounds(xMin, xMax, yMin, yMax)
		# THE PROCESS

		# Perform Box Select ->
			# Initialize the box select
				# this - retrieves the world transform, inverts it, and retrieves a projection matrix from the camera
				# as well as sets the start mouse position
			# With the matrix in hand, we calculate the normalized xy coords for each object in the scene

		# on release, we EndBoxSelect ->
			# set the end mouse position
			# Calculate the boundary of the bounding box

			# loop through our objects 

	def GetInstancePositions(self):
		cues = parent.Main.op('Cues').ops('base_Cue*')

		for i in cues:
			newPos = tdu.Position(i.par.Tx.eval(), i.par.Ty.eval(), 0.0)

			self.ObjectPositions.update({i.path : newPos})
		
		# pprint(self.SelectableObjectsBounds)


	def PerformBoxSelect(self,startUV):
		self.InitiateBoxSelect(startUV)

		for key, position in self.ObjectPositions.items():
			self.ObjectPositionsNormalized.update({key : self.CalcNormalizedXYCoordsForObject(position)})
	
	def InitiateBoxSelect(self, startUV):
		self.ws2vs = self.MainCam.worldTransform
		self.ws2vs.invert()
		self.vs2ndcs = self.MainCam.projection( parent.Main.width , parent.Main.height )
		self.StartMousePos = startUV

	def CalcNormalizedXYCoordsForObject(self, pos):

		pos = self.ws2vs * pos

		pos = self.vs2ndcs * pos
		finalX = pos.x * .5 + .5
		finalY = pos.y * .5 + .5
		# calc normalized val
		return (finalX,finalY)
	

	def EndBoxSelect(self,endUV, clearOld = True):
		self.EndMousePos = endUV
		# set the bounding box
		self.CalcSelectionMinMaxBoundary()

		if clearOld:
			self.Selection.clear()

		for key, pos in self.ObjectPositionsNormalized.copy().items():
			curOp = op(key)
			
			if curOp != None:

				isInside = self.TestObjectXYCoords(pos)
				
				if isInside:
					
					self.Selection.insert(0, op(key))
			else:
				self.ObjectPositionsNormalized.pop(key)

		self.DoSelection(self.Selection,self.OldSelection)

	def CalcSelectionMinMaxBoundary(self):

		self.SelectionBounds = self.Bounds(
			min( self.StartMousePos[0] , self.EndMousePos[0] ),
			max( self.StartMousePos[0] , self.EndMousePos[0] ),
			min( self.StartMousePos[1] , self.EndMousePos[1] ),
			max( self.StartMousePos[1] , self.EndMousePos[1] )
			)


	def TestObjectXYCoords(self, objXYCoords):
		xTest = objXYCoords[0] > self.SelectionBounds.xMin and objXYCoords[0] < self.SelectionBounds.xMax
		yTest = objXYCoords[1] > self.SelectionBounds.yMin and objXYCoords[1] < self.SelectionBounds.yMax
		isInsideBox = xTest and yTest
		return isInsideBox
		
	def DoSelection(self, selectionList, oldSelection, select = True):
		# print('new: ', selectionList)
		# print('old: ', oldSelection)

		newSel = set(selectionList)
		oldSel = set(oldSelection)
		
		

		# # print(newSel)
		# print('new selection', newSel)
		# print('old selection', oldSel)

		dif = oldSel - newSel



		for i in dif:
			if i != None:
				i.par.Selectionindex = -1
				i.par.Selected = False
	

		for ind, obj in enumerate(selectionList):
			if obj != None:
					
				obj.par.Selected = select
				
				if select:
					obj.par.Selectionindex = ind
				else:
					obj.par.Selectionindex = -1
