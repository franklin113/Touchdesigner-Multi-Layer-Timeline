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
class Transformer:
	"""
	Transformer description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.renderPickOp = self.myOp.op('renderpick1')

		self.System = ipar.SystemSettings
		self.User = ipar.UserSettings
		self.KeyboardOp = parent.Main.op('Input/Keyboard')
		self.CueBounds = namedtuple('CueBounds', ['xMin','xMax','yMin','yMax'])
		self.MainCam = parent.Main.op('Render/cam1')
		self.MainComp = parent.Main
		self.Manager = parent.Main.op('Project')

		self.SelectedBounds = None
		self.NextBounds = None
		self.PrevBounds = None
		self.TimePosition = self.MainComp.op('select_CurrentTime')['timer_fraction_WorldPos']
		self.Playhead = op('/Multi_Layer_Timeline/Timeline3D/Canvas/geo_Playhead')
		self.SnapLineGeo = self.MainComp.op('Canvas/geo_SnapLine')
		self.SnappingDistance = 1	# this is set in the render pick extension

	def IsOutsideBounds(self, boundsObj, newPosition):
		distance = 20 * self.System.Orthorenderaspect.eval()
		outsideX = False
		outsideY = False
		upDown = 0
		leftRight = 0
		# (xMin = xMin, yMin = yMin, xMax = xMax, yMax = yMax)
		if newPosition[0] < boundsObj[0] - distance:
			outsideX = True
			leftRight = -1
		if newPosition[0] > boundsObj[2] - distance:
			outsideX = True
			leftRight = 1

		if newPosition[1] < boundsObj[1] - distance:
			
			outsideY = True
			upDown = -1
		if  newPosition[1] > boundsObj[3] + distance:

			outsideY = True
			upDown = 1

		return (outsideX, outsideY, leftRight, upDown)

	def GetBounds(self,tx,ty, endTime):
		cueHeight = self.User.Cueheight.eval()

		xMin = tx
		xMax = endTime
		yMin = ty - cueHeight * .5
		yMax = ty + cueHeight * .5
		bounds = (xMin, yMin, xMax, yMax, ty)
		# print('coming from getBounds- len(',len(bounds))
		# (xMin = xMin, yMin = yMin, xMax = xMax, yMax = yMax, xMinCenterY)
		return bounds

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

	def FetchBounds(self):
		return self.myOp.fetch('AllCueBounds', list(),storeDefault = True)

	def UpdateAllBounds(self):
		cues = self.Manager.GetOps(cue = True)
		boundsList=  []
		for i in cues:
			tx = i.par.Tx.eval()
			ty = i.par.Ty.eval()
			endTime = i.par.Computedendtime.eval()
			bounds = self.GetBounds(tx,ty,endTime)
			boundsList.append((i, bounds)) # append a tuple, the op and the bounds object

		# add the playhead to the bounds list
		curTimePos = self.MainComp.op('select_CurrentTime')
		playheadBounds = (self.Playhead, (self.TimePosition.eval(),0,0,0,0))
		boundsList.append(playheadBounds)
		boundsList.sort(key=lambda x: x[1][0])

		# print('coming from Update all - len(',len(boundsList[0][1]))
		
		# for i in boundsList:   # FOR TESTING 
		# 	print(i[1][0])
		success = self.StoreBounds(listToReplace=boundsList)
		if success:
			return boundsList
		else:
			print('Failed to store bounds data')

	def PrintBounds(self, bounds, title = 'Bounds'):
		print('---------')
		print(title)
		for i in bounds:
			print(i[0].name, round(i[1][0],3))
		print('---------')

	def IncrementalTransform(self, vals, incr=None):
		
		if not incr:
			incr = op('null_RoundingValues')['chan1'].eval()
		
		xyzVals = [round(vals[x] / incr) * incr for x in range(len(vals))]
		return xyzVals

	def UvToPixel(self, u=0, v=0, delta=False):
		# stolen directly from kantan mapper
		if self.renderPickOp:
			renderOp = self.renderPickOp.par.rendertop.eval()
			camera = renderOp.par.camera.eval()
			w = parent.Main.width #renderOp.width
			h = parent.Main.height #renderOp.height
			camTransform = camera.localTransform
			s, r, t = camTransform.decompose()
			camS = s[0]
			camTx = t[0]
			camTy = t[1]
			camOrtho = camera.par.orthowidth
			ratio = camOrtho / w

			if not delta:
				u = (u*2-1)/2
				v = (v*2-1)/2
				u = u * camOrtho * camS + t[0]
				v = v * h * ratio * camS + t[1]
			else:
				u = u * camOrtho * camS
				v = v * h * ratio * camS

		return [int(u),int(v)]

	def WorldspaceTimeConversions(self, worldPosX = None, timePos = None):
		timelineWidth = self.System.Computedtimelinewidth.eval()
		timelineLength = self.User.Timelinelength

		unitsPerSecond = timelineWidth / timelineLength

		#print('full width: ', timelineWidth)

		if timePos != None:
			return timePos * unitsPerSecond - timelineWidth * .5

		if worldPosX != None:
			return worldPosX #/ unitsPerSecond + timelineLength * .5

		#print(unitsPerSecond)

	def PositionToTime(self, worldSpacePosition):
		
		return self.WorldspaceTimeConversions(worldPosX = worldSpacePosition)

	def TimeToPosition(self, timePosition, clampTime = True):
		# converts seconds to position in worldspace

		timelineLength = self.User.Timelinelength.eval()

		if timePosition > timelineLength and clampTime:
			timePosition = timelineLength
		

		return self.WorldspaceTimeConversions(timePos = max(0, timePosition))

	def WorldspaceToScreenSpace(self, x=0,y=0,z=0):
		# need this info for creating the proper projection matrix.
		WidthOfRender = self.MainComp.width
		HeightOfRender = self.MainComp.height

		# build the matrix we need to convert from world space to projection space.
		cam = self.MainCam
		cam_viewMatInv = cam.worldTransform
		cam_viewMatInv.invert()
		cam_projMat = cam.projection(WidthOfRender,HeightOfRender)
		mat_world_2_ndc = cam_projMat * cam_viewMatInv

		# creating a tdu.position object, we only care about X, so using 0's for y and z.
		pos_ws = tdu.Position( x , y , z )

		# two matrix mult steps taking that point from world space, to ndc projection space. (-1:1)
		pos_ps = mat_world_2_ndc * pos_ws

		# calculate the pixel coordinate of the right edge of the cue.
		x_max_ps = pos_ps.x
		x_max_ss = tdu.remap( x_max_ps , -1 , 1 , 0 , WidthOfRender )
		x_max_ss = int(round(x_max_ss)) # this is an integer value in the range of 0 : WidthOfRender

		return x_max_ss


	def ScreenSpaceToWorldspace(self, x=0, y=0, offset = None):		
		'''
			Description - general purpose, convert pixel space / screen space to worldspace
			x, y - pixel coordinates
			z is automatically assigned a 0 value
			offset is a pixel count as a tuple to return the worldspace count of

			One use case for offset is if you want to count how many units 50 pixels is.
			Set x as the width of our render, offset as 50.

			returns tdu.Position(x,y,z)

		'''
		WidthOfRender = self.MainComp.width
		HeightOfRender = self.MainComp.height


		viewMatrix = self.MainCam.worldTransform 
		viewMatrix.invert()  				# create a view matrix
		projMatrix = self.MainCam.projection(WidthOfRender,HeightOfRender)	# create a projection matrix

		newMat = projMatrix * viewMatrix	# multiply projection matrix by view matrix
		newMat.invert()						# invert the results

		# convert original x,y pixel coords to NDC space 
		ndc_x = tdu.remap(x, 0, WidthOfRender, -1, 1)
		ndc_y = tdu.remap(y, 0, HeightOfRender, -1,1)

		ndc_pos = tdu.Position(ndc_x,ndc_y,0)	# create position object from ndc based vector

		ws_pos = newMat * ndc_pos	

		if offset:
			# convert original x,y pixel coords to NDC space 
			ndc_x2 = tdu.remap(x-offset[0], 0, WidthOfRender, -1, 1)
			ndc_y2 = tdu.remap(y-offset[1], 0, HeightOfRender, -1,1)
			
			ndc_pos2 = tdu.Position(ndc_x2 ,ndc_y2 , 0)	# create position object from ndc based vector

			ws_pos2 = newMat * ndc_pos2	

			return ws_pos - ws_pos2 #(ws_pos.x - ws_pos2.x, ws_pos.y - ws_pos.y, 0)

		return ws_pos
	
	# def Get_SS_2_WS_Offset(self, xOffset= 0, yOffset = 0):
	# 	'''
	# 		Find the number of worldspace units will fit inside of a pixel distance
	# 		takes either an x offset or yOffset, pixels
	# 		returns a worldspace unit count
	# 	'''
		
		
	# 	WidthOfRender, HeightOfRender = 0,0

	# 	if xOffset:
	# 		WidthOfRender = self.MainComp.width
	# 	if yOffset:
	# 		HeightOfRender = self.MainComp.height

	# 	if xOffset and yOffset:
	# 		print("Data clipped: Can only process x or y. Not Both! Returning X")

	# 	startPos = self.ScreenSpaceToWorldspace(x= WidthOfRender, y= HeightOfRender)
	# 	endPos = self.ScreenSpaceToWorldspace(x= WidthOfRender - xOffset, y= HeightOfRender - yOffset)
	# 	delta = 0

	# 	if xOffset:
	# 		delta = startPos.x - endPos.x
	# 	elif yOffset:
	# 		delta = startPos.y - endPos.y
	# 	return delta
		