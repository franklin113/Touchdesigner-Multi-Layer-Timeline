
class CueSpec:

    def __init__(self, Cuetype = None, Title=None, Imagefile=None, Thumbnail=None, Cuelength = None, Starttime = None, Backgroundcolor = None, Layer = None , customTypePage = None):
        self.Cuetype = Cuetype          # default will be 'Media'
        self.Title = Title              # default is "Cue" + the comps digits
        self.Imagefile = Imagefile      
        self.Thumbnail = Thumbnail      # default is one of the sample images 
        self.Cuelength = Cuelength      # a generic time based on screen space 
        self.Starttime = Starttime      # will be the location where you released the mouse
        self.Backgroundcolor = Backgroundcolor      # default is blue
        self.Layer = Layer                      # the layer the mouse was released over
        self.CustomTypePage = customTypePage    # default is None, you can create custom cues here