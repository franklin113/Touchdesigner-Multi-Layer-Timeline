"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""
		# # properties
		# TDF.createProperty(self, 'MyProperty', value=0, dependable=True,
		# 				   readOnly=False)

		# # stored items (persistent across saves and re-initialization):
		# storedItems = [
		# 	# Only 'name' is required...
		# 	{'name': 'StoredProperty', 'default': None, 'readOnly': False,
		# 	 						'property': True, 'dependable': True},
		# ]
		
		# # stored items (persistent across saves and re-initialization):
		# storedItems = [
		# 	# Only 'name' is required...
		# 	{'name': 'StoredProperty', 'default': None, 'readOnly': False,
		# 	 						'property': True, 'dependable': True},
		# ]
		# Uncomment the line below to store StoredProperty. To clear stored
		# 	items, use the Storage section of the Component Editor
		
		# self.stored = StorageManager(self, ownerComp, storedItems)


# from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
TDJ = op.TDModules.mod.TDJSON
import json

from pprint import pprint

from collections import OrderedDict

class Manager:
	"""
	Manager description

	Manages the overall state and performs operations like Add item, remove item

	Maintains references to all items


	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp
		self.TemplateOp = parent.Main.op('Cues/base_Template_Cue0')
		self.newOpName = 'base_Cue0'
		self.CueSpec = mod.CueSpec.CueSpec(Title='Tim')
		self.CuesOp = parent.Main.op('Cues')
		self.LayersOp = parent.Main.op('Layers')
		self.UserSettingsOp = parent.Main.op('iparUserSettings')
		self.CurrentTimeOp = parent.Main.op('select_CurrentTime')
		self.TimeOp = parent.Main.op('Time')
		self.RenderPickComp = parent.Main.op('RenderPick')
		
		self.DefaultNumLayers = 5
		self.DefaultLength = 30
		self.DefaultZoom = 1
		self.DefaultCamPosition = 0
		self.DefaultFPS = 60
		self.TimelineMenu = {'Labels':[],'Names':[]}
		self.Clipboard = []
		self.ThumbnailCache = self.CuesOp.op('base_CacheBuilder')
		# TDF.createProperty(self, 'MyProperty', value=0, dependable=True,
		# 			readOnly=False)


	### Cue Creation

	def AddDropped(self, dropUV, cueSpecList):
		newOpsList = []
		renderOp = parent.Main.op('Render')

		dropPosWS = renderOp.UVSpaceToWorldspace(u = dropUV[0], v = dropUV[1])
		
		timePos = dropPosWS.x
		vertDropPos = dropPosWS.y
		layer = parent.Main.op('RenderPick').WorldspaceToLayer(vertDropPos)
		
		ui.undo.startBlock('Add Dropped () - ' + self.myOp.path)


		for ind, icueSpec in enumerate(cueSpecList):

			icueSpec.Starttime = timePos
			icueSpec.Layer = layer
			if timePos > ipar.UserSettings.Timelinelength.eval():
				break
			newOp = self.AddCue(cueSpec = icueSpec, requiresThumbnail=False)
			newOpsList.append(newOp)

			timePos += icueSpec.Cuelength

		
		
		self.RenderPickComp.ext.Selection.Selection = newOpsList
		self.RenderPickComp.ext.Selection.DoSelection(self.RenderPickComp.ext.Selection.Selection, self.RenderPickComp.ext.Selection.OldSelection, select = True)
		
		self.ThumbnailCache.AddItem(newOpsList, isMulti=True)
		ui.undo.endBlock()

	def AddCue(self, cueType = 'Media', name = None, cueSpec = None, copyOp = None, requiresThumbnail = True):
		'''
			This method will add cues or layers

			Who calls Add? This could be a drag and drop, a button
			
			When you add a cue you want it to have a task. Media cue, command cue, internal command cue,

			CueType can be 'Media', 'Script', 'Internal'

			cueSpec: can assign any of the cues parameters via a dictionary

		'''
		sourceOp = None

		if copyOp:				# we can copy a cue
			sourceOp = copyOp
		else:
			sourceOp = self.TemplateOp	# or we can create a new cue from the template


		newOp = self.CuesOp.copy(sourceOp, name=self.newOpName)
		newOp.tags.add('CueItem')

		newOp.nodeY = 200 * -newOp.digits

		if type(cueSpec) == type(self.CueSpec):
			
			# run through all the parameters and assign them with setattr
			for i in newOp.customPars:
				curParName = i.name
				if hasattr(cueSpec,curParName):
					print('has it!')
					curAttr = getattr(cueSpec,curParName)
					if curAttr != None:
						setattr(newOp.par, curParName, curAttr)
			
			
		self.CuesOp.op('base_Library/opfind1').cook(force=True)
		
		#self.RenderPickComp.UpdateAllBounds()
		# print(project.pythonStack())
		if requiresThumbnail:
			self.ThumbnailCache.AddItem(newOp)

		return newOp

	def AddDefault(self, startTime = None, layer=None, requiresThumbnail = True):
		'''
			Allows you to easily create a basic cue.
			a cueSpec is a python module that allows you to quickly create an object to use with our constructor
			cueSpec can be found next to this extension

		'''
		defaultWidth = parent.Main.op('Render').ScreenSpaceToWorldspace(offset= [500,0]).x
		cueSpec = mod.CueSpec.CueSpec(Starttime= startTime, Layer = layer, Cuelength = defaultWidth)

		newOp = self.AddCue(cueSpec = cueSpec)

		return newOp

	def CopyOperation(self):
		# find out what is selected
		self.Clipboard = list(self.RenderPickComp.ext.Selection.Selection)
		self.RenderPickComp.ext.Selection.OldSelection = list(self.Clipboard)
		
		# we have on occasion gotten none type objects, so we will jsut clearn them out
		for i in self.Clipboard:
			if i == None:
				self.Clipboard.remove(i)
		
		try:
			self.Clipboard.sort(key=lambda a: a.par.Starttime.eval())
		except AttributeError as e:
			print("Error during copy operation: ", e)
			print(self.Clipboard)
		# print(self.Clipboard)

	def PasteOperation(self):
		
		#add a cue based on the copied ops
		ui.undo.startBlock('Paste Operation () - ' + self.myOp.path)
		
		currentTime = self.CurrentTimeOp['timer_fraction_WorldPos'].eval()
		initialTime = self.Clipboard[0].par.Starttime.eval()
		newCues=[]
		
		for i in self.Clipboard:

			newCue = self.AddCue(copyOp=i, requiresThumbnail = False)
			timeOffset = i.par.Starttime.eval() - initialTime
			newCue.par.Starttime= currentTime + timeOffset
			newCues.append(newCue)
		
		self.ThumbnailCache.AddItem(newCues, isMulti=True)
		
		self.RenderPickComp.ext.Selection.Selection = list(newCues)

		self.RenderPickComp.ext.Selection.DoSelection(self.RenderPickComp.ext.Selection.Selection, self.RenderPickComp.ext.Selection.OldSelection, select = True)
		
		# self.RenderPickComp.DoSelection(newCues, self.RenderPickComp.OldSelection, select = True)

		# self.RenderPickComp.UpdateAllBounds()
		# self.RenderPickComp.ext.Selection.Selection = newCues
		
		ui.undo.endBlock()
		
		pass
	### END Cue Creation

	### Cue Destruction

	def UndoRemoveCues(self, isUndo, deletedCues):
		'''
			undo block callback
			cleans up our selection because it can get a bit buggy
			It just clears selection

		'''
		self.ThumbnailCache.AddItem(deletedCues,isMulti=True)
		self.CuesOp.CookCueReferences()
		for i in deletedCues:
			i.par.Selected = False
			i.par.Selectionindex = -1

		#self.RenderPickComp.UpdateAllBounds()
		
	

		parent.Main.op('RenderPick').Selection.clear()

	def RemoveCues(self, selection= True, cueOps = None, clearAll = False):
		'''
			Descr
			Allows you to remove cues in a few ways:
			clearAll removes all cues. Useful for when you are creating a new timeline
			selection, the default, is great for just hitting the delete button
			cueOps could be used for if you have deleted some other way

			UNDO BLOCK - We have implimented an undo feature here, 
				if you delete a cue, you can hit undo. It will call the UndoRemoveCues callback

		'''
		ui.undo.startBlock('Remove Cues () - ' + self.myOp.path)
		
		if clearAll:
			self.ThumbnailCache.DeleteItem(0, clear = True)
			for i in self.GetOps(cue=True):
				
				
				i.destroy()
		
		if cueOps:
			ui.undo.addCallback(self.UndoRemoveCues,list(cueOps))
			
			for i in cueOps:
				self.ThumbnailCache.DeleteItem(i)
				
				i.destroy()
		
		
		if selection:
			SelectionOp = parent.Main.op('RenderPick')
			selectedCues = SelectionOp.Selection
			
			ui.undo.addCallback(self.UndoRemoveCues,list(selectedCues))
			self.ThumbnailCache.DeleteItem([x.digits for x in selectedCues],isMulti=True)
		
			for ind, curOp in enumerate(selectedCues):
				if curOp != None:

					if curOp.name != self.TemplateOp.name: # just make sure somehow it's not the template. it should never be, but...
						
						
						curOp.destroy()
				else:
					selectedCues.pop(ind)

			SelectionOp.Selection.clear()
		# self.RenderPickComp.UpdateAllBounds()
		ui.undo.endBlock()

		# self.ThumbnailSetup(replaceAll= True,delay = 1)
		self.CuesOp.op('base_Library/opfind1').cook(force=True)
	

		return

	### END Cue Destruction



	### User Settings
	def SetDefaultUserSettings(self):
		ipar.UserSettings.Timelinelength = self.DefaultLength
		ipar.UserSettings.Layercount = self.DefaultNumLayers
		ipar.UserSettings.Fps = self.DefaultFPS

	### END User Settings

	### Timeline Creation

	def AddTimeline(self, name):


		if name in self.TimelineNames or name == '':
			print('Timeline already exists')
			return False

		else:
			self.StoreTimelineData()
			
			self.ActiveTimeline = name

			allNames = self.TimelineNames
			allNames.add(name)
			self.TimelineNames = allNames
			
			self.myOp.store('TimelineNames',self.TimelineNames) # we don't have a settr for self.TimelineNames
			
			self.RemoveCues(clearAll=True)	# reset the cues 

			self.SetDefaultUserSettings()	# start from scratch on some user settings

			self.StoreTimelineData()
			return True

	def DeleteTimeline(self, timelineName):

		allNames = self.TimelineNames
		allNames.remove(timelineName)
		self.TimelineNames = allNames

		self.ActiveTimeline = ''

		timelines = self.Timelines
		timelines.pop(timelineName)
		self.myOp.store('Timelines',timelines)				# the actual Json data

		self.RemoveCues(clearAll = True)


	### END Timeline Creation

	### GET SET Item Info
	def GetItemData(self, opList, excludePages = set(),parsToExclude = set()):

		assert opList != None or opList != [], "Empty list passed to GetItemData"

		
		cuesDict = OrderedDict()


		for curItem in opList:
			
			parWriterObj = mod.ParWriter.ParWriter(curItem)
			cuesDict[curItem.name] = parWriterObj.ConvertToJsonable(excludePages = excludePages)

		return cuesDict

	def SetItemData(self, opToSet, jsonDict):
		pWriter = mod.ParWriter.ParWriter(opToSet)
		pWriter.UpdatePars(jsonDict= jsonDict)

	def GetOps(self,layer=False,cue=False, user=False):
		# Retrieves a list of all our cues in our scene

		if cue:
			listOfCues = self.CuesOp.findChildren(tags= ['CueItem'])
			return listOfCues
		elif layer:
			listOfLayers = self.LayersOp.findChildren(tags= ['LayerItem'])
			return listOfLayers
		elif user:
			return [parent.Main.op('iparUserSettings')]
		else:
			return []

	def GetSystemData(self):
		
		system = parent.Timeline

		systemInfo = {
			'Version' : system.par.Version.eval(),
			'Author' : system.par.Author.eval(),
			'AuthorEmail' : system.par.Authoremail.eval(),
			'TD_Build' : project.saveBuild,
			'OS_Name' : project.saveOsName,
			'OS_Version' : project.saveOsVersion
		}
		
		return systemInfo

	def GetTimelineData(self):
		cues = self.GetOps(cue=True)
		layers = self.GetOps(layer=True)
		userSettings = self.GetOps(user=True)

		cueData = self.GetItemData(cues,excludePages={'System'})
		layerData = self.GetItemData(layers, excludePages={'System'})

		userData = self.GetItemData(userSettings, excludePages = {'Project'})

		timelineData = {
			'Cues' : cueData,
			'Layers' : layerData,
			'User' : userData,
			'TimePosition' : self.CurrentTimeOp['timer_fraction_WorldPos'].eval()
		}
		return timelineData
	### END GET SETE Item Info

	### STORE AND LOAD TIMELINE INFO
	def StoreTimelineData(self, timelineName=None, resetState = False):
		if not timelineName:
			timelineName = ipar.UserSettings.Activetimeline.eval()
		
		if resetState == True:
			ipar.UserSettings.Activetimeline = ''
			self.TimelineNames = set()
			self.myOp.store('Timelines', {})

			return


		allNames = self.TimelineNames	 #self.AddTimelineNameToSet(timelineName)
		allNames.add(timelineName)
		self.TimelineNames = allNames

		# self.UpdateTimelineMenu(timelineName)
		currentTimelineData = self.GetTimelineData()

		timelines = self.Timelines
		timelines.update({timelineName : currentTimelineData})

		self.myOp.store('Timelines', timelines)

	def LoadTimeline(self, timelineName, savePrevious = True):
		'''
			Description: 
			timelineName: a string, the name of the timeline to load

				The standard wat this will work is the user presses "Load Timeline" on the control panel. 
				The timelineName is provided by the parexec callback
				You will automatically load the item selected in the Available timelines dropmenu

			loading CLEARS ALL YOUR CUES! Make sure everything is saved before loading!
		'''
		
		# Save project on exit

		timelines = self.Timelines 					# all your timelines' data

		toLoadTimeline = timelines[timelineName]	# the timeline we are loading up

		activeTimelineBeforeLoad = self.ActiveTimeline 		# the timeline active prior to our load
		
		if savePrevious:
			self.StoreTimelineData(activeTimelineBeforeLoad)	# store the current timeline before we load
		# print('save')
		cuesList = toLoadTimeline['Cues']										
		layerList = toLoadTimeline['Layers']
		userList = toLoadTimeline['User']
		currentTime = toLoadTimeline['TimePosition']

		###### REMOVE CUES #### DANGER ZONE #####
		self.RemoveCues(selection=False, clearAll=True)							# start from scratch with cues removed
		################################################
		
		numCues = len(cuesList)			# to determine how many cues we will add

		## Add cues
		
		newCueList = [self.AddDefault(requiresThumbnail=False) for x in range(numCues)]		# add the correct number of cues.

		self.ThumbnailCache.AddItem(newCueList, isMulti=True)

		for curCue in newCueList:				
			curJsonDict = cuesList[curCue.name]		# the jsoned object for the cue
			self.SetItemData(curCue,curJsonDict)	# set all the custom parameters to the cue

		## Update user settings
		self.SetItemData(self.UserSettingsOp,userList['iparUserSettings']) # set user settings

		## Update layers
		self.UpdateLayerInfo(layerList)	# made it an extra method because I think I may need to delay this


		
		ipar.UserSettings.Activetimeline = timelineName
		ipar.UserSettings.Availabletimelines = timelineName
		self.TimeOp.GotoTime(seconds = currentTime)


	def UpdateLayerInfo(self, layerData):
		numLayers=  len(layerData)
		presentLayers = self.GetOps(layer=True)
		for curLayer in presentLayers:
			curJsonDict = layerData[curLayer.name]
			self.SetItemData(curLayer,curJsonDict)

	### END Store and Load Timeline INfo

	### Project File Management
	def PackageProject(self):


		user = self.GetOps(user = True)
		userData = self.GetItemData(user, excludePages = {'Settings','Camera'}, parsToExclude=set(('Activeproject','Activetimeline','File')))	# we only want the project page
		systemData = self.GetSystemData()

		projData = {
			'UserSettings' 	: userData,
			'SystemData' 	: systemData,
			'Timelines'		: self.Timelines,
			}

		# pprint(jsonProj)

		return projData
		# ext.Saver.SaveToDisk(data = projData)

	def LoadProject(self,saveBeforeExit=True):
		
		if saveBeforeExit:
			print('save before exit enabled')
			self.StoreTimelineData()
			ext.Saver.SaveToDisk(filepath = ipar.UserSettings.Activeproject.eval())


		self.SetSystemToDefault()
		projectData = ext.Saver.LoadFromDisk()
		
		# print('Timelines', projectData['Timelines'])
		if projectData == None or projectData == dict():
			debug("Failed To Retrieve Data From Disk")
			return
		else:
			print('Loading Project')
		try:
			self.myOp.store('Timelines',projectData['Timelines'])
		except Exception as e:
			print("Error storing Timelines while loading project")
			debug(e)


		run("ipar.UserSettings.Activeproject = ipar.UserSettings.File.eval()",delayFrames=1,fromOP = me)
			

		try:
			names = list(projectData['Timelines'].keys())
			firstTimeline = None
			for i in names:
				if i != '' and i != ' ':
					firstTimeline = i
					break
			self.TimelineNames = set(names)
			
		except Exception as e:
			print("Could not assign timeline names, invalid project data?", e)

		run("op('{}').LoadTimeline('{}',savePrevious=False)".format(self.myOp,firstTimeline),delayFrames=5)

		

		'''	
			Steps to loading a project: 
			1) Set the Timeline data in storage
			2) Set the User's Project page settings
			3) Update the TimelineNames member property

		'''
		# pprint(project.pythonStack())


	def CloseProject(self, saveBeforeExit=True):
		
		if saveBeforeExit:
			self.StoreTimelineData()
			ext.Saver.SaveToDisk(filepath = ipar.UserSettings.Activeproject.eval())

		self.SetSystemToDefault()
		ipar.UserSettings.Activeproject = ''
		ipar.UserSettings.File = ''

	def SetSystemToDefault(self):
		self.StoreTimelineData(resetState=True)
		###### REMOVE CUES #### DANGER ZONE #####
		self.RemoveCues(selection=False, clearAll=True)							# start from scratch with cues removed
		################################################

	### END Project File Management


	@property
	def TimelineNames(self):
		curSet =self.myOp.fetch('TimelineNames',set(),storeDefault=True)
		# self.UpdateTimelineMenu(curSet)
		return curSet
	
	@TimelineNames.setter
	def TimelineNames(self, val):
		assert type(val) == set, "Wrong type assigned to TimelineNames. Expected a set, got a " + str(type(val))

		self.myOp.store('TimelineNames',val)
		valList = list(val)

		menuLabels = [x for x in valList if x != '']

		menuNames = menuLabels



		menu= ipar.UserSettings.Availabletimelines
		menu.menuNames = menuLabels
		menu.menuLabels = menuNames
		menu.val = self.ActiveTimeline

		return 

	@property
	def ActiveTimeline(self):
		return ipar.UserSettings.Activetimeline.eval()

	@ActiveTimeline.setter
	def ActiveTimeline(self,val):
		ipar.UserSettings.Activetimeline.val = val

	@property
	def Timelines(self):
		return self.myOp.fetch('Timelines', dict(), storeDefault = True)

	### END REGION STORE ITEM DATA

