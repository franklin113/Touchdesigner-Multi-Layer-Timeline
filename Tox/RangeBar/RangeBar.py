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

class RangeBar:
	"""
	RangeBar description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		self.Bar = self.ownerComp.op('container2')

		self.LAnchor = self.Bar.par.leftanchor
		self.RAnchor = self.Bar.par.rightanchor

		self.LRange = self.ownerComp.par.Lrange
		self.RRange = self.ownerComp.par.Rrange
		self.InitialClickU = 0
		self.InitialInsideClickU = 0
		self.AnchorsOnClick = ()
		self.ButtonClicked = -1

		self.RangeComp = parent.Timeline.op('Timeline3D/Render/iparCamera')
		# assert self.RangeComp

	def ChangeRange(self,channel,val,prev):
		delta = 0
		currentU = parent().panel.insideu.val

		delta = currentU-self.InitialClickU


		if self.ButtonClicked == 0:
			if self.RAnchor.val - self.LAnchor.val <= .025 and delta > 0:
				return
			newVal = self.AnchorsOnClick[0] + delta
			newVal = max(0, min(newVal,self.RAnchor.val-.001))

			self.LAnchor.val = newVal
			self.LRange.val = newVal


		elif self.ButtonClicked == 1:
			newVal1 = self.AnchorsOnClick[0] + delta
			newVal2 = self.AnchorsOnClick[1] + delta

			if newVal2 > 1 or newVal1 < 0:
				return

			self.LRange.val = newVal1
			self.RRange.val = newVal2

			self.LAnchor.val = newVal1
			self.RAnchor.val = newVal2

		elif self.ButtonClicked == 2:
			if self.RAnchor.val - self.LAnchor.val <= .025 and delta < 0:
				return
			newVal = self.AnchorsOnClick[1] + delta
			newVal = min(1, max(newVal,self.LAnchor.val+.001))
			self.RAnchor.val = newVal
			self.RRange.val = newVal
		parent().par.Sliderwidth.val = self.Bar.width
		pass