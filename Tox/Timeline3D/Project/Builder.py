
class Builder:

    def __init__(self):

        self.ObjTypes = {
            'CueItem'   : parent.Main.op('Cues/base_Template_Cue0'),
            'LayerItem' : parent.Main.op('Layers/Template_layer1'),
            'TimeCompItem'  : parent.Main.op('Time')
        }

    def BuildObj(self, objType: str):
		## Buildes an object of the given type
    	self.ObjTypes[objType].AddNew()
