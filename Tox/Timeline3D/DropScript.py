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

    def __init__(self, Cuetype = None, Title=None, Imagefile=None, Thumbnail=None, Cuelength = None, Starttime = None, Backgroundcolor = None, Layer = None ):

        self.Cuetype = Cuetype
        self.Title = Title
        self.Imagefile = Imagefile
        self.Thumbnail = Thumbnail
        self.Fadeinout1 = Fadeinoutduration[0]
        self.Fadeinout2 = Fadeinoutduration[1]
        self.Cuelength = Cuelength
        self.Starttime = Starttime
        self.Backgroundcolor = Backgroundcolor
        self.Layer = Layer

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
        for file in selectedFiles:
        #     ### Build new CueSpec keyword dict
        #     ### We handle time position and layer internally so just leave those out
            cueSpecArgs = {
                'Cuetype'   : 'Media',
                'Title'     : file.Name,
                'Imagefile' : file.Path,
                'Thumbnail' : file.Thumb,
                'Cuelength' : file.Seconds,
                'Backgroundcolor' : None,
            }

        #     create the cueSpec
            cueSpec = op('Project').mod.CueSpec.CueSpec(**cueSpecArgs)
            
        #     # Provide the UV coords and a desired cueSpec
            cueSpecList.append(cueSpec)
            
        # this takes your info and creates teh cue
        op('Project').AddDropped(dropPos, cueSpecList)
        

drop = PerformDrop(args)