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

class Mouse:
	"""
	Mouse description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.InputOp = parent.Input
		self.keyboardOp = self.InputOp.op('Keyboard')
		self.UserSettings = ipar.UserSettings
		self.SystemSettings = ipar.SystemSettings
		self.RenderPickOp = parent.Main.op('RenderPick')
		self.PanelChop = op('panelOnScreen')
		self.MainComp = parent.Main
		self.renderOp = parent.Main.op('RenderPick/renderpick1').par.rendertop.eval()
		self.camera = self.renderOp.par.camera.eval()

		self.mainOp = parent.Main

		self.ScrollConstantChop = self.myOp.op('constant_VerticalScroll')
		self.WheelNull = self.myOp.op('null_Wheel')

		self.UV = (0,0)
		self.CamPos = ipar.UserSettings.Cameraposition.eval()

		self.newUV = (0,0)

		self.matrix = tdu.Matrix()
		
		self.CurZoom = self.UserSettings.Zoom.eval()
		self.ZoomOp = self.myOp.op('select_NormalizedTimelinelength1') # ????
		self.TimelineLengthNormalized = self.myOp.op('select_NormalizedTimelinelength')
		self.VertScrollMax = self.myOp.par.Verticalscrollmax
		self.ScrollInverted = ipar.UserSettings.Invertscroll
		self.VerticalScrollInverted = ipar.UserSettings.Invertverticalscroll

	def Zoom(self, val, prev):

		'''
			Description - 
			We are thinking in terms of cutting off a certain amount of pixels per zoom.
			To do this, we are converting 100 pixels to worldspace. Our RenderPickOp's 
			'Transformer' extension contains some useful methods for this. 
			ScreenSpaceToWorldSpace is one such useful method.
			It can convert a single vector/position or provide a width of units

			To get a width of units, put a tuple in the offset keyword argument
			
			
			important variables---
			offset: this is the number of world units inside 100 pixels.
			zoomConstant: value we are multiplying our multiplier by
			zoomMultiplier: 1 / (timelineLength / offset)
			finalZoom: final assignment
		'''

		## -- Get settings
		timelineLength = self.UserSettings.Timelinelength.eval()
		zoomSpeed = self.UserSettings.Zoomspeed.eval()
		WidthOfRender = self.MainComp.width
		oldZoom = self.UserSettings.Zoom.eval()

		
		valueSign = (val)	# positive or negative

		offset = self.RenderPickOp.ScreenSpaceToWorldspace(x=0, offset = (100,0) )
		offset = offset.x	# we only need the x value
		
		if valueSign > 0: 	# the incoming offset is  double the value when zooming in
			zoomConstant = 2 * zoomSpeed
		else:
			zoomConstant = 4 * zoomSpeed

		# this is how we are creating our zoom multiplier
		zoomMultiplier = 1 / (timelineLength / offset)

		calcedZoom = zoomConstant * zoomMultiplier

		calcedZoom *= valueSign

		newZoom = oldZoom + calcedZoom
		finalVal = max(1, min(2,newZoom))	
		
		# final zoom assignment
		self.UserSettings.Zoom = finalVal



	def Scroll(self, val, prev, vertical = False):
		timelineLength = self.UserSettings.Timelinelength.eval()
		
			
		if self.WheelNull['inside'].eval() == 0:
			return

		if vertical:
			maxScroll = self.VertScrollMax.eval()
			curScroll = self.ScrollConstantChop['verticalScroll'].eval()


			offset = self.RenderPickOp.ScreenSpaceToWorldspace(y=0, offset = (0,20) )
			scrollVal = offset.y	# we only need the x value

			valueSign = val	
			
			scrollVal *= valueSign * (int(not self.VerticalScrollInverted.eval()) * 2 - 1) # process incoming scroll direction and user settings
			
			finalVal = max( 0, min(maxScroll, scrollVal + curScroll))

			self.ScrollConstantChop.par.value0 = finalVal

			return
		
		

		# we are calculating how many worldspace units are within the scroll speed constant.
		# Scroll speed is in pixels
		# Technically, we have a little weirdness going on because we are doing some math in chops to stop
		# the camera from falling off the edges. It doesn't seem that noticable though, so I'm leaving as is. 
		WidthOfRender = self.MainComp.width
		
		# the number of pixels in the range
		offset = self.RenderPickOp.ScreenSpaceToWorldspace(x=0, offset = (self.SystemSettings.Scrollspeed.eval(),0) )
		
		scrollVal = offset.x

		valueSign = (val) * (int(not self.ScrollInverted.eval()) * 2 - 1)		# invert the mouse direction	
		
		scrollVal *= valueSign				# make it either -val or +val

		# don't let it fly off the edge!
		finalVal = max(0, min(timelineLength,self.UserSettings.Cameraposition.eval() + scrollVal))
		
		# do final assignment
		self.UserSettings.Cameraposition = finalVal