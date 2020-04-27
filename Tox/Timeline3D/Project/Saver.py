
# from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
from datetime import datetime

import os
from shutil import copyfile
import json
class Saver:
	"""
	Saver description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp
		self.ProjectFile = ipar.UserSettings.File
		self.SaveBackups = ipar.UserSettings.Savebackups
		self.PreviouslySavedFilePath = None #parent().fetch('LastSavedPath', None, storeDefault=True)

		# Test Data
		# self.myOp.store('Project', json.loads(json.dumps({'TestA' : 'Data', 'TestB' : "Data2"})))

	def SaveToDisk(self, data = None, filepath=None):
		'''
			Save files to disk
			data will be our json data for our project

			We have a toggle to save backups or not in the user settings.
			If enabled, we will run the portion below about saving backups..

		'''
		newRelativePath = None

		if filepath: 
			newRelativePath = filepath

		else:
			newRelativePath = self.ProjectFile.eval()
		if not newRelativePath:
			print("Error saving timelines, no file path provided")
			return False	
			print(newRelativePath)
		
		ipar.UserSettings.Activeproject = newRelativePath

		joinedPath = os.path.join(project.folder, newRelativePath)
		filepath =  os.path.normpath(joinedPath)
		directory, name = os.path.split( filepath )

		if not data:
			data = self.myOp.PackageProject()

		serializedData = json.dumps(data,indent = 4)

		# print('dir: ', directory)
		# print('name: ', name)

		# if backups is enabled and we have saved before..
		# we init the extension to None, so it shouldn't run on first save
		if self.SaveBackups.eval() and self.PreviouslySavedFilePath:
			backupPath = os.path.join(directory, 'TimelineBackup')
			backupPath = os.path.normpath(backupPath)
			
			try:
				os.makedirs(backupPath)
				debug("Building backup path here: '", backupPath,"'")

			except FileExistsError:
				pass

			timeStamp = self.GetTimestamp()		# TOD

			prevDir, prevExt = os.path.splitext(self.PreviouslySavedFilePath)	# path where we last saved, extension

			oldDir, oldName = os.path.split(prevDir)	# get only the directory, and the name, no extension

			newPath = os.path.join(backupPath, oldName + timeStamp + prevExt)	# get valid path
			try:
				copyfile(self.PreviouslySavedFilePath,newPath)		# copy the old file to the backup folder
			except FileNotFoundError as e:
				print("Invalid target location while trying to copy Primary file to backup file")
		# filename = os.path.join(directory, self.ProjectFile.eval())
		# filename = os.path.normpath(filename)


		try:
			with open(filepath, 'w') as projectFile:
				projectFile.write(serializedData)
				self.PreviouslySavedFilePath = name
				parent().store('LastSavedPath',name)

		except Exception as e:
			print("Error saving timelines: ", e)
			return False

		return True

	def LoadFromDisk(self):
		Loadable = False
		relFilePath = self.ProjectFile.eval()
		fullPath = os.path.join(project.folder, relFilePath)
		fullPath = os.path.normpath(fullPath)
		# projectData = None
		try:
			with open(fullPath, 'r') as projectFile:
				projectRawJson = projectFile.read()
				jsonObj = json.loads(projectRawJson)
				Loadable = True
		except Exception as e:
			print("Error loading file: ", e)
			Loadable = False

		if Loadable:
			
			self.myOp.store('Project', jsonObj)
			return jsonObj
		else:
			return None

	def GetTimestamp(self):
		now = datetime.now()
		timeString = now.strftime("---%m-%d-%Y--%H-%M-%S")
		return timeString