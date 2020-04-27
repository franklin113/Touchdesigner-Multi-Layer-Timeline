"""
# events - a list of named tuples with the fields listed below.
# eventsPrev - a list of events holding the eventsPrev values.
#
#	u				- The selection u coordinate.			(float)
#	v				- The selection v coordinate.			(float)
#	select			- True when a selection is ongoing.		(bool)
#	selectStart		- True at the start of a selection.		(bool)
#	selectEnd		- True at the end of a selection.		(bool)
#	selectedOp		- First picked operator.				(OP)
#	selectedTexture	- Texture coordinate of seleectedOp.	(Position)
#	pickOp			- Currently picked operator.			(OP)
#	pos				- 3D position of picked point.			(Position)
#	texture			- Texture coordinate of picked point.	(Position)
#	color			- Color of picked point.				(4-tuple)
#	normal			- Geometry normal of picked point.		(Vector)
#	depth			- Post projection space depth.			(float)
#	instanceId		- Instance ID of the object.			(int)
#	row				- The row associated with this event	(float)
#	inValues		- Dictionary of input DAT strings for the given row, where keys are column headers. (dict)
#	c


"""
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
from collections import namedtuple
class RenderPick:
	"""
	RenderPick description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp


		self.AllCueBounds = self.myOp.fetch('AllCueBounds', dict(),storeDefault = True)
		self.SelectedBounds = None
		
		self.InstanceId = -1

		self.ObjectPrefix = {
			'Cue' : 'base_Cue',
			'Layer' : 'base_Layer',
			'Bg' : 'geo_Timeline_'
		}

		self.PageScope = {
			'Cue' : 'Settings',
			'Layer' : 'Layer',
			'Bg' : 'Settings Camera Project'
		}

		self.RickClickCallbackInfo = {
			'Tag' : None,
			'Op' : None
		}

		self.PreviousTag = ''

		self.System = ipar.SystemSettings
		self.User = ipar.UserSettings

		self.StartTimes = []
		self.Durations = []

		self.ClickPosition = tdu.Position()
		self.ClickMapUV = tdu.Position()

		self.MainOp = parent.Main
		self.MasterComp = parent.Timeline


		self.UserSettingsOp = self.MainOp.op('iparUserSettings')
		self.ParComp = self.MainOp.par.Parametercomp.eval()
		self.KeyboardOp = parent.Main.op('Input/Keyboard')
		self.TimeComp = parent.Main.op('Time')
		self.Timer = self.TimeComp.op('timer1')
		self.CueDB = parent.Main.op('Cues/null_CueDB')
		self.CanDragVertically = True
		self.CanStretch = False
		self.CanTranslate = True

		self.VerticalDragRegion = (.2, .8)
		self.HorizontalStretchRegion = 1
		self.LayerIncrementThreshold = .0
		# in pixels, the amount of screen space from the right edge of a cue, that can be selected for edge grab.
		self.edgeGrabWidthInPixels = 10

		self.ClickType = 0
		self.MouseOp = self.MainOp.op('Input/Mouse')
		self.BoxSelectOp = self.MainOp.op('Canvas/geo_BoxSelect')

		self.SnapStartMouseXPos = None
		self.SnapState = False
		self.PrevSnapState = False

	def EventSelectStart(self, renderPickDat, event, eventPrev):
		'''	
			Description: Here we handle interactions on initial click

			A Cue, Layer, BG, or Scrubbar can be selected.

			Cue: 
				A cue item, assign parameters values based on conditions
			
				Parameters:
					Start Time -> (tx)
					Cue Length -> (sx)

				How do we know what cue is selected? 
					self.InstanceId -> event.instanceId

				Types of interactions:
					Translate -> Change time position
					Stretch -> Change length

		'''

		self.ClickType = int(event.inValues['aux'])
		selectedOp = event.selectedOp.parent()
		if not selectedOp:	# sometimes this gets called without an object
			return

	

		self.InstanceId = event.instanceId
		ext.Selection.OldSelection = list(ext.Selection.Selection)
		self.ClickMapUV = event.texture
		self.ClickPosition = event.pos
		self.IsScrubBar = False
		self.IsTimelineItem = False  # we will use this to determine what kinds of interactions we need to perform
		self.IsBoxSelect = False



		if 'Cue' in selectedOp.tags: # Selection is a cue
			tag = 'Cue'
			objPrefix = self.ObjectPrefix[tag]
			self.PreviousTag = tag
			


			self.ParComp.par.pagescope = self.PageScope[tag]	# change our UI page

			self.IsTimelineItem = True	# we use this during our next render pick stage
			
			selectedItem = self.GetObject(selectedOp, self.InstanceId, tag) # retrieve the component this cue represents
			if self.ClickType == 4:

				self.RickClickCallbackInfo.update( {
					'Tag' : tag,
					'Op' : selectedItem
				})

				try:
					self.MasterComp.Callbacks.OnRightClick(self.RickClickCallbackInfo)
				except:
					pass

				return
			
			elif self.ClickType == 2:
				
				self.SetTimer(gotoTime=True,seconds=selectedItem.par.Starttime.eval())
			
			uvAspect = selectedItem.par.Uvaspect.eval()
			
			timelineLength = self.MainOp.op('Canvas/null_Settings')['normalizedLength'].eval()


			### -------Lucas added this stuff ------------ ###
			### - The matrix transform method was moved to Transformer extension

			# convert the computedEndTime which is worldSpace pos of right edge of cue, to the integer/pixel coordinate in screen space.
			cue_x_max_ss = ext.Transformer.WorldspaceToScreenSpace( selectedItem.par.Computedendtime.eval() , 0 , 0 )

			# this variable is the min position in pixels of the stretch drag area.
			# by making it 10 pixels less than the right edge's position, we have a fixed width defined by a min and max now.
			cue_x_min_ss = cue_x_max_ss - self.edgeGrabWidthInPixels

			# get the pixel X coordinate of where we clicked.
			click_x_ss = ext.Transformer.WorldspaceToScreenSpace( self.ClickPosition[0] , 0 , 0 )

			# boolean and logic, combined gives us true only if clicked pixel is with in the range of our defined drag area.
			IsClickStretch = click_x_ss > cue_x_min_ss and click_x_ss <= cue_x_max_ss

			ext.Transformer.SnappingDistance = ext.Transformer.ScreenSpaceToWorldspace(x=0, offset = (20,0)).x	# we only need the x value
			### ----------------------------------------------------------###

			# ---- PROCESS INTERACTION TYPES -------- #
			# print(self.ClickMapUV.x, 1.0 - finalStretchRegion)
			# if self.ClickMapUV.x > 1.0 - finalStretchRegion : # STRETCH
			if IsClickStretch : # STRETCH
				
				self.CanStretch = True
				self.CanDragVertically = False
				self.CanTranslate = False
			
			else:	# START TIME CHANGE
				self.CanStretch = False
				self.CanDragVertically = True
				self.CanTranslate = True
			# ----- PROCESSED INTERACTION ------------- #

		elif 'Layer' in selectedOp.tags:
			tag = 'Layer'
			objPrefix = self.ObjectPrefix[tag]
			selectedItem = self.GetObject(selectedOp, self.InstanceId, tag)

			self.PreviousTag = tag
			
			if self.ClickType == 4:

				self.RickClickCallbackInfo.update( {
					'Tag' : tag,
					'Op' : selectedItem
				})

				try:
					self.MasterComp.Callbacks.OnRightClick(self.RickClickCallbackInfo)
				except:
					pass
				return

			self.ParComp.par.pagescope = self.PageScope[tag]

		elif 'Bg' in selectedOp.tags:
			tag = 'Bg'
			self.PreviousTag = tag
			if self.ClickType  == 1:
				self.ParComp.par.op = self.UserSettingsOp
				# objPrefix = self.ObjectPrefix[tag]
				# selectedItem = self.GetObject(selectedOp, objPrefix, self.InstanceId)

				self.ParComp.par.pagescope = self.PageScope[tag]
				ext.Selection.Selection.clear()
				ext.Selection.DoSelection(ext.Selection.Selection, ext.Selection.OldSelection, select = True)
				return
			elif self.ClickType == 4:
				ext.Selection.PerformBoxSelect((event.u,event.v))

				self.BoxSelectOp.par.tx, self.BoxSelectOp.par.ty = event.pos.x , event.pos.y
				run("op('{}').render = True".format(self.BoxSelectOp),delayFrames= 1)
				self.IsBoxSelect = True

				return
		elif 'Scrub' in selectedOp.tags:
			
			self.IsScrubBar = True

			if self.ClickType == 4:

				self.RickClickCallbackInfo.update( {
					'Tag' : 'Scrubbar',
					'Op' : None
				})
				try:
					self.MasterComp.Callbacks.OnRightClick(self.RickClickCallbackInfo)
				except:
					pass
				return

			# if we are alt clicking the scrubbar


			# if self.ClickType == 2:
			# 	uv = (float(event.inValues['u']), float(event.inValues['v']))
			# 	self.MouseOp.UV = uv
			# 	self.MouseOp.CamPos = self.ClickPosition.x#ext.Transformer.UvToPixel(u = uv[0], v = [uv[1]]) #.MainOp.op('Render/cam1').par.tx.eval()
			# 	print('click pos : ', self.ClickPosition)
			return
		else:
			ext.Selection.Selection.clear()
			ext.Selection.DoSelection(ext.Selection.Selection, ext.Selection.OldSelection, select = True)
			selectedItem = None
			return
		
		
		self.ParComp.par.op = selectedItem

		#debug(objPrefix + str(self.InstanceId))
		try:
			ind = ext.Selection.Selection.index(selectedItem)
			ext.Selection.Selection.pop(ind)

		except:
			pass

		if not self.System.Multiselect.eval():
			ext.Selection.Selection = [selectedItem]
			
		else:
			ext.Selection.Selection.insert(0,selectedItem)

		self.AllCueBounds = self.myOp.fetch('AllCueBounds')
		ext.Selection.DoSelection(ext.Selection.Selection, ext.Selection.OldSelection, select = True)


		if self.IsTimelineItem:
			self.ProcessSelectedCues(event.pos)


		pass

	def EventSelect(self, renderPickDat, event, eventPrev):
		

		currentClickPosition = event.pos

		UV = event.texture	# TDU.Position
		prevUV = eventPrev.texture	# TDU.Position

		outsideX, outsideY, directionX, directionY = False, False, 0, 0

		if self.ClickType == 1: # Left Click
			if self.IsTimelineItem:	# if we are dragging a cue - 
				
				try:
					self.SelectedBounds = self.myOp.GetBounds(ext.Selection.Selection[0].par.Tx.eval() ,ext.Selection.Selection[0].par.Ty.eval(), ext.Selection.Selection[0].par.Cuelength.eval())
					outsideX, outsideY, directionX, directionY = self.myOp.IsOutsideBounds(self.SelectedBounds,currentClickPosition)
				except Exception as e:
					print(e)
				if event.pickOp == None:
					return

				newGeoPosition = None

				for ind, obj in enumerate(ext.Selection.Selection):
					

					if self.CanTranslate: # Translate our cue

						newGeoPosition = currentClickPosition + self.ClickPositionOffsets[ind]  # TDU.Position
						# self.SetStartTime(newGeoPosition.x, obj)
						proposedStartTime = newGeoPosition.x
						# ext.Transformer.StoreBounds(singleEntry = (obj, self.SelectedBounds),swapEntryIndex=ext.Selection.Selection[0].par.Timeorderindex.eval())
						comparedToNeighborTest = ext.Transformer.CompareNeighbors(proposedStartTime, ext.Selection.Selection[0].par.Timeorderindex.eval(),currentClickPosition.x, self.SnapStartMouseXPos)
						
						# CompareNeighbors returns ( did we snap ? , updated Time position, the yPosition you should set your line to)
						
						if comparedToNeighborTest[0] == True:
							self.SnapState = True

							if self.PrevSnapState == False:
								# print('we know we just started to snap')
								self.SnapStartMouseXPos = currentClickPosition.x

							self.PrevSnapState = True
							ext.Transformer.SetSnapLines( comparedToNeighborTest[1],  comparedToNeighborTest[2][0], comparedToNeighborTest[2][1])
							ext.Transformer.RenderSnappingLines(True)
						else:
							self.SnapStartMouseXPos = None
							self.SnapState = False
							self.PrevSnapState = False
							ext.Transformer.RenderSnappingLines(False)

							# print('setting to 0')

						self.SetStartTime(comparedToNeighborTest[1], obj)

					
					elif self.CanStretch: # Stretch our cue

						curTime = currentClickPosition + self.OffsetFromEndTime[ind]
						deltaTime = curTime.x - obj.par.Computedendtime.eval()
						self.SetLength(obj, deltaTime, addTo = True)

					if outsideY and self.CanDragVertically:	# change the layer of our cue
						
						curLayer = obj.par.Layer
						layerCount = self.User.Layercount.eval()

						if min(self.Layers) + directionY >= 0 and max(self.Layers) + directionY < layerCount:
							obj.par.Layer += directionY

				self.Layers = [x.par.Layer.eval() for x in ext.Selection.Selection]

			elif self.IsScrubBar:	# move our playhead

				if event.pickOp == None:
					return
				
				if self.ClickType == 1:
					if self.KeyboardOp.par.Onlyalt.eval():
						self.User.Cameraposition = event.pos.x
					else:
						timePosition = self.myOp.PositionToTime(currentClickPosition.x)
						timePosition = min(self.User.Timelinelength.eval(),timePosition)
						
						if self.KeyboardOp.par.Ctrl.eval():	# snap the playhead to time markers
							timePosition = ext.Transformer.IncrementalTransform([timePosition])[0]

						self.TimeComp.GotoTime(seconds = timePosition)
					

			

		elif self.ClickType == 4:	# Right Click
		
			if self.IsBoxSelect: # perform our box selection

				delta = self.ClickPosition - currentClickPosition
				self.BoxSelectOp.par.sx = delta[0]
				self.BoxSelectOp.par.sy = delta[1]


	def EventSelectEnd(self, renderPickDat, event, eventPrev):

		
		# Reset all snapping data to False
		self.SnapStartMouseXPos = None
		self.SnapState, self.PrevSnapState = False, False
		ext.Transformer.RenderSnappingLines(False)

		if self.IsBoxSelect:
			# if we are cleaning up our box selection - 

			self.BoxSelectOp.render = False		# disable rendering of box select geo
			
			ext.Selection.EndBoxSelect((event.u,event.v), clearOld = not self.KeyboardOp.par.Shift.eval())

			self.ClickType = 0					

			ext.Selection.GetInstancePositions()
			
			# revert Position back to 0,0 
			self.BoxSelectOp.par.Offsetx , self.BoxSelectOp.par.Offsety = 0,0
			self.BoxSelectOp.par.tx , self.BoxSelectOp.par.ty = 0,0

		if self.IsScrubBar:
			ext.Transformer.UpdateAllBounds()

		pass

	
	def SetStartTime(self, startTime, Cue):

		if Cue.par.Lock.eval():
			return

		realStartTime = max(0.0,startTime)
		realStartTime = min(realStartTime, self.User.Timelinelength.eval() - 1)

		if self.KeyboardOp.par.Ctrlalt.eval():
			realStartTime = min(self.User.Timelinelength.eval()-1, self.Timer['timer_seconds0'].eval())


		elif self.KeyboardOp.par.Ctrl.eval():		# snap to seconds
			# realStartTime = int(realStartTime)
			realStartTime = ext.Transformer.IncrementalTransform([realStartTime])[0]

		elif self.KeyboardOp.par.Alt.eval():		# snap to frames
			frameLength = 1000 / self.User.Fps.eval() * .001
			realStartTime = self.myOp.IncrementalTransform( [realStartTime], frameLength)[0]


		Cue.par.Starttime = realStartTime

	def SetLength(self, obj, time, addTo = False):
		
		if obj.par.Lock.eval():
			return

		realLength = time

		if self.KeyboardOp.par.Ctrl.eval():		# snap to seconds
			realLength = int(realLength)

		elif self.KeyboardOp.par.Alt.eval():		# snap to frames
			frameLength = 1000 / self.User.Fps.eval() * .001
			realLength = self.myOp.IncrementalTransform( [realLength], frameLength)[0]
		
		# realLength = max(.005, realLength)

		if addTo:
			obj.par.Cuelength += realLength
		else:
			obj.par.Cuelength = realLength


	def GetObject(self, selectedOp, instanceId, tag):
		
		prefix = self.ObjectPrefix[tag]
		
		if tag == 'Cue':
			opName = self.CueDB[instanceId+2,'name']
		
		else:
			opName = prefix + str(instanceId)

		return selectedOp.parent().op(opName)

	def SetTimer(self, gotoTime=None, segment = None, seconds = None, frame = None, fraction = None):
		'''
			Description - 
				Here we can set the values for our timer
				
				keyword args:
					gotoTime: sets the time position of our timer in various ways.
						an example would be using the current world position as the seconds
		'''
		if gotoTime:

			self.Timer.goTo(segment = segment, seconds = seconds, frame = frame, fraction = fraction)



	def ProcessSelectedCues(self,eventPos):
		self.StartTimes = []
		self.Durations = []
		self.OriginalPositions = []
		self.ClickPositionOffsets = []
		self.Layers = []
		self.OffsetFromEndTime = []
		self.ClickPosition = eventPos		# tdu.Position
		
		for i in ext.Selection.Selection:
			curStartTime = i.par.Starttime.eval()
			curCueLength = i.par.Cuelength.eval()
			curObjPositionX = i.par.Tx.eval()
			curObjPositionY = i.par.Ty.eval()
			curLayer = i.par.Layer.eval()
			curEndTimePos = i.par.Computedendtime.eval()

			self.Layers.append(curLayer)
			self.StartTimes.append(curStartTime)
			self.Durations.append(curCueLength)
			self.OriginalPositions.append((curObjPositionX,curObjPositionY))
			self.ClickPositionOffsets.append(tdu.Vector(curObjPositionX - self.ClickPosition))
			self.OffsetFromEndTime.append(tdu.Vector(curEndTimePos - self.ClickPosition))