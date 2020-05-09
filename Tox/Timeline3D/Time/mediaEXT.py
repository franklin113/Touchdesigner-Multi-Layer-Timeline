class Player:


    def __init__(self, ownerComp):
        '''
        Media class to help manage video loading, unloading and playback functions
        '''
        self.Owner = ownerComp
        self.Timer = ownerComp.op('timer1')
        self.MoviePlayers = ownerComp.ops('moviefilein*')
        self.CueTable = ownerComp.op('select_Library')
        self.CueParser = ownerComp.op('cueParser')



    def Preload(self, movieTOP=None, filePath='', layerNum=None):
        '''
        Player.Preload is based on TouchDesigner's preload() method and adds additional logic for loading a filepath
        into a specific moviefileinTOP.
        :param movieTOP:  This is the TOP to preload
        :type movieTOP: moviefileinTOP
        :param filePath: Filepath points to the video file being preloaded
        :type filePath: str
        :param layerNum: This is to identify which TOP is being targeted in a timeline-layered system.
        :type layerNum: int
        :return: None
        :rtype:
        '''
        if movieTOP:
            movieTOP.par.file.val = filePath
            movieTOP.preload()
            movieTOP.par.index.expr = "op('{}')['timer_seconds{}']".format(self.Timer.name, layerNum)

    def Unload(self, movieTOP=None, allFiles=False):
        '''
        Player.Preload is based on TouchDesigner's unload() method and adds additional logic for unloading a filepath
        in a specific moviefileinTOP
        :param movieTOP: This is the TOP to unload
        :type movieTOP: moviefileinTOP
        :param allFiles: Additional logic for unloading all moviefileinTOPs in the list of Player.MoviePlayers
        :type allFiles: bool
        :return: None
        :rtype:
        '''
        if movieTOP:
            movieTOP.par.play = 0
            movieTOP.par.file = ''
            movieTOP.unload(cacheMemory=True)
            movieTOP.par.index.expr = ''
        elif allFiles:
            for player in self.MoviePlayers:
                self.Unload(movieTOP=player)

    def LoadPreset(self):
        '''
        Player.LoadPreset looks for Layers, Start Times, and row numbers ready to be preloaded
        :return: None
        :rtype:
        '''
        s = self.CueParser
        chopChanData = s.chans()
        if 'begin' in [chan.name for chan in chopChanData]:
            layers, startTimes, rows = chopChanData
            for layer, startTime, row in zip(layers.vals, startTimes.vals, rows.vals):
                layerNum = int(layer)
                if layerNum >= 0:
                    filePath = self.CueTable[int(row)+1, 'Imagefile'].val
                    movieTOP = self.MoviePlayers[layerNum]
                    timelineLayer = int(row+1)
                    self.Preload(movieTOP=movieTOP, filePath=filePath, layerNum=timelineLayer)
                else:
                    self.Unload(allFiles=True)

    def Play(self, movieTOP):
        '''
        Players.Play starts playing the targeted moviefileinTOP
        :param movieTOP: This is the TOP to play
        :type movieTOP:  moviefileinTOP
        :return:  None
        :rtype:
        '''
        movieTOP.par.play = 1

    def GetMoviePlayerFromRow(self, segment):
        '''
        Player.GetMoviePlayerFromRow helps to find which moviefileinTOP being referenced
        :param segment: The segment number == the segmentDAT row number.
                        The segment (row) number is used to get the layer number
                        The layer number is used as in index into the Player.MoviePlayers list
        :type segment: int
        :return: moviefileinTOP
        :rtype:
        '''
        rowNumber = segment
        if rowNumber:
            playerLayerNum = int(self.CueTable[rowNumber, 'Layer'].val)
            movieTOP = self.MoviePlayers[playerLayerNum]
            return movieTOP

    def StartPlaying(self, movieFileInTOP):
        '''
        Switch movieFileInTOP par.play to 1
        '''
        movieFileInTOP.par.play = 1