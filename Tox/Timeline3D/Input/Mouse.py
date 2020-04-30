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

		self.newUV = (0,0)

		self.matrix = tdu.Matrix()
		
		self.CurZoom = self.UserSettings.Zoom.eval()
		self.ZoomOp = self.myOp.op('select_NormalizedTimelinelength1') # ????
		self.TimelineLengthNormalized = self.myOp.op('select_NormalizedTimelinelength')
		self.VertScrollMax = self.myOp.par.Verticalscrollmax
		self.ScrollInverted = ipar.UserSettings.Invertscroll
		self.VerticalScrollInverted = ipar.UserSettings.Invertverticalscroll

