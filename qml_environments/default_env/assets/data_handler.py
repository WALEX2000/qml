import pandas as pd
import pickle
from os import path

def readCSV(dataPath):
    return pd.read_csv(dataPath)

class DataHandler:
    """Class used to handle data in the pipeline context"""
    @staticmethod
    def load(dataPath):
        """Given the path of the data, loads and returns its handler"""
        head, tail = path.split(dataPath)
        handlerPath = head + "/data_conf/" + tail + ".handler"
        if(not path.exists(handlerPath)): return None
        with open(handlerPath, 'rb') as handlerFile:
            dataHandler : DataHandler = pickle.load(handlerFile)
        dataHandler.setDataPath(dataPath)

        return dataHandler

    def __init__(self, targetVarName, scoringFunc, dataPath="", readDfFunc=pd.read_csv, testRatio=0.25):
        self._targetVarName = targetVarName
        self._scoringFunc = scoringFunc
        self._readDfFunc = readDfFunc
        self._testRatio = testRatio
        self._dataframe = None
        self._dataPath = dataPath
    
    def setDataPath(self, dataPath):
        self._dataPath = dataPath

    def getDataframe(self):
        if(self._dataframe is not None): return self._dataframe
        self._dataframe = self._readDfFunc(self._dataPath)
        return self._dataframe
    
    def getSplit(self):
        df = self.getDataframe()
        test_data = df.sample(frac=self._testRatio, random_state=77)
        train_data = df.drop(test_data.index)

        X_train = train_data.drop(self._targetVarName, axis = 1)
        Y_train = train_data.loc[:,self._targetVarName]
        X_test = test_data.drop(self._targetVarName, axis = 1)
        Y_test = test_data.loc[:,self._targetVarName]

        return X_train, X_test, Y_train, Y_test

    def score(self, trueLabels, predictions):
        return self._scoringFunc(trueLabels, predictions)
    
    def save(self, handlerPath):
        self._dataframe = None # The whole point is that the data is not saved here, but stays on the file        
        with open(handlerPath, 'wb') as handlerFile:
            pickle.dump(self, handlerFile)