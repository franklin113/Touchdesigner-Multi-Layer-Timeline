"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""
import numpy as np
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class Render:
	"""
	Render description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		self.MainCam = parent.Main.op('Render/cam1')
		self.MainComp = parent.Main
		self.uvChans = [op('panel1')['insideu'], op('panel1')['insidev']]
		self.ScrollSpeed = ipar.SystemSettings.Scrollspeed
		self.TimelineLength = ipar.UserSettings.Timelinelength
		self.ZoomSpeed = ipar.UserSettings.Zoomspeed

		self.RangeBar = parent.Timeline.op('container_RangeSlider/container2')
		self.lRangePar, self.rRangePar = ipar.Camera.Lrange, ipar.Camera.Rrange
		self.SnappingThresholdPar = parent.Main.op('Cues/base_Snapping/script1').par.Threshold

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
	
	def UVSpaceToWorldspace(self, u=0, v=0, offset = None):		
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
		ndc_x = tdu.remap(u, 0, 1, -1, 1)
		ndc_y = tdu.remap(v, 0, 1, -1,1)

		ndc_pos = tdu.Position(ndc_x,ndc_y,0)	# create position object from ndc based vector

		ws_pos = newMat * ndc_pos	

		if offset:
			# convert original x,y pixel coords to NDC space 
			ndc_x2 = tdu.remap(u-offset[0], 0, WidthOfRender, -1, 1)
			ndc_y2 = tdu.remap(v-offset[1], 0, HeightOfRender, -1,1)
			
			ndc_pos2 = tdu.Position(ndc_x2 ,ndc_y2 , 0)	# create position object from ndc based vector

			ws_pos2 = newMat * ndc_pos2	

			return ws_pos - ws_pos2 #(ws_pos.x - ws_pos2.x, ws_pos.y - ws_pos.y, 0)

		return ws_pos
	

	def Zoom(self, val,prev):
		if val == 0:
			return
		timelineLength = ipar.UserSettings.Timelinelength.eval()
		
		uv =	self.GetUV()										# the mouse uv when I scroll
		uv2ws = self.UVSpaceToWorldspace(u=uv[0])		# convert screenspace to world space

		newXPos = uv2ws[0]
		normalized_newXPos = tdu.remap(newXPos,0,ipar.Camera.Resolutionx.eval(),0,1)	# normalized worldspace

		

		viewRanges = (self.lRangePar.eval(), self.rRangePar.eval())		# Retrieve View range custom parameters

		offset = self.ScreenSpaceToWorldspace(x=0, offset = (100,0) )
		offset = offset.x	# we only need the x value

		zoomSpeed = self.ZoomSpeed.eval()
	
		if val > 0: 	# the incoming offset is  double the value when zooming in
			zoomConstant = zoomSpeed
		else:
			zoomConstant = zoomSpeed + 2
			
		# this is how we are creating our zoom multiplier
		zoomMultiplier = 1 / (timelineLength / offset)
		# get the distance between targets
		distancesToTarget = [normalized_newXPos - viewRanges[0], normalized_newXPos - viewRanges[1]]

		thisZoomLength = zoomConstant * zoomMultiplier * val

		newLRange = max( 0, min(viewRanges[0] + distancesToTarget[0] / zoomConstant * val, 1))
		newRRange = max( 0, min(viewRanges[1] + distancesToTarget[1] / zoomConstant * val, 1))
		
		self.SetRange(newLRange,newRRange)

		### Do stuff that requires calculations based on zoom level...
		self.SnappingThresholdPar.val = offset * .25


	def Scroll(self, val, prev, vertical = False):
		'''
			1) Get width of 100 pixels
			2) normalize the value
			3) find out if we should move left or right
			4) add/sub the values to the LRange and RRange parameters
		'''
		if val == 0:
			return
		if vertical:
			vScrollPar = ipar.Camera.Camypos
			maxScroll = ipar.SystemSettings.Maxscrollv.eval()
			curScroll = vScrollPar.eval()


			offset = self.ScreenSpaceToWorldspace(y=0, offset = (0,20) )
			scrollVal = offset.y	# we only need the x value

			valueSign = val	
			
			scrollVal *= valueSign * (int(not ipar.UserSettings.Invertverticalscroll.eval()) * 2 - 1) # process incoming scroll direction and user settings
			
			finalVal = max( 0, min(maxScroll, scrollVal + curScroll))

			vScrollPar.val = finalVal

			return
		else:
			# Process user settings
			val *= ipar.UserSettings.Invertscroll.eval() * 2. - 1

			# start by getting the worldspace width of N pixels. N = Scrollspeed parameter
			WidthOfRender = self.MainComp.width
			offset = self.ScreenSpaceToWorldspace(x=0, offset = (self.ScrollSpeed.eval(),0) ).x
			offset_Norm = tdu.remap(offset, 0, self.TimelineLength.eval(), 0, 1)
			offset_Norm *= val

			lRangePar= ipar.Camera.Lrange
			rRangePar= ipar.Camera.Rrange

			lRangeVal = lRangePar.eval()
			rRangeVal = rRangePar.eval()

			newL= 0
			newR= 0

			newR = rRangeVal + offset_Norm
			newL = lRangeVal + offset_Norm

			if val > 0:
				if rRangePar.eval() + offset_Norm > 1:
					newOffset = 1 - rRangeVal
					newR = 1
					newL = min(lRangeVal + newOffset,1)


			elif val < 0:
				if lRangePar.eval() + offset_Norm < 0:
					newOffset = lRangePar.eval() 
					newL = 0
					newR = max(0, rRangeVal - newOffset)


			self.SetRange(newL, newR)

	def GetUV(self):
		uvs = list(self.uvChans)
		return (uvs[0].eval(),uvs[1].eval())

	def SetRange(self, newLRange, newRRange):
		self.lRangePar.val = newLRange
		self.rRangePar.val = newRRange
		
		if newRRange - newLRange < .015:
			return

		self.RangeBar.par.leftanchor.val = newLRange
		self.RangeBar.par.rightanchor.val = newRRange