
class CueSpec:

    def __init__(self, Cuetype = None, Title=None, Imagefile=None, Thumbnail=None, Fadeinoutduration  : tuple = (None,None), Cuelength = None, Starttime = None, Backgroundcolor = None, Layer = None ):

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