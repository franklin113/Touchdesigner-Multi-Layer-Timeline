#
#  arguments for dropping nodes           (and files)
#
#       args[0] dropped node name            (or filename)
#       args[1] x position
#       args[2] y position
#       args[3] dragged index
#       args[4] total dragged
#       args[5] operator                     (or file extension)
#       args[6] dragged node parent network  (or parent directory)
#       args[7] dropped network
#

#### ---  Example of dropping a lister row into the stage --- ####

'''
class CueSpec:

class CueSpec:

    def __init__(self, Cuetype = None, Title=None, Thumbnail=None, Cuelength = None, Starttime = None, Backgroundcolorr = None, Backgroundcolorg = None, Backgroundcolorb = None, Layer = None , customTypePage = None):
        self.Cuetype = Cuetype
        self.Title = Title
        self.Thumbnail = Thumbnail
        self.Cuelength = Cuelength
        self.Starttime = Starttime
        self.Backgroundcolorr = Backgroundcolorr
        self.Backgroundcolorg = Backgroundcolorg
        self.Backgroundcolorb = Backgroundcolorb
        self.Layer = Layer
        self.CustomTypePage = customTypePage
'''

# playerOp = op.Playback


#CueSpecPath = op('Project').mod.CueSpec.CueSpec()

def GetRowData(mediaBin):
    selectedDat = mediaBin.op('out_selected')
    selectedRows = selectedDat.rows()[1:]
    return selectedRows



def PerformDrop(args):
    droppedOpName = args[0]
    droppedOpPath = args[6]
    if droppedOpName == parent(2).par.Lister.eval().name:
        mediaBin = op(droppedOpPath).op(droppedOpName)
        selectedFiles = mediaBin.SelectedRowObjects

        # don't touch this - sets the position
        dropPos = (parent().panel.insideu, parent().panel.insidev)
        cueSpecList = []
        specializedSpecList = []
        for file in selectedFiles:
        #     ### Build new CueSpec keyword dict
        #     ### We handle time position and layer internally so just leave those out
            cueSpecArgs = {
                'Cuetype'   : 'Media',
                'Title'     : file.Name,
                'Thumbnail' : file.ThumbTOPPath,
                'Cuelength' : file.Seconds,
            }

            specializedSpecArgs = {
                'Moviefile' : file.Path
            }

        #     create the cueSpec
            cueSpec = op('Project').mod.CueSpec.CueSpec(**cueSpecArgs)
            
        #     # Provide the UV coords and a desired cueSpec
            cueSpecList.append(cueSpec)
            specializedSpecList.append(specializedSpecArgs)
            
        # this takes your info and creates teh cue
        op('Project').AddDropped(dropPos, cueSpecList, specializedSpecList)
        

drop = PerformDrop(args)