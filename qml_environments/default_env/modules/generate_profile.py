import pandas as pd
from modules.general_utils import CLIexecSync
from qml_environments.default_env.modules.inspect_data import getInfoFromDataPath, getMetadata, saveMetadata, metaInfoTemplate, hashFile
from os import path
import pickle
#from mlprimitives.datasets import Dataset

def getDataset(filePath : str):
    dataset = None
    with open(filePath, 'r') as datasetFile:
        dataset = pickle.load(datasetFile)
    if(dataset is None): return
    df = pd.concat([dataset.data, dataset.target], axis=1)
    print(df)
    # Save dataset to tmp file
    # Return string to tmp file
    pass

# getDataset("/Users/alexandrecarqueja/Desktop/Tese/qml/EXPERIMENTS/Exp2/data/winequality-BLUE.dataset")

def runEvent(event):
    if(event.is_directory is True): return
    (_, profilePath, profileTitle, fileExtension, metaPath) = getInfoFromDataPath(event.src_path)
    if(fileExtension == '.tmp' or fileExtension == '.DS_Store'): return

    hash = hashFile(event.src_path)
    metaDict = getMetadata(metaPath)
    if(metaDict is None): return # Only generate profile for tracked files
    elif(metaDict.get('pandas_profile_hash') == hash and path.exists(profilePath)): return
    metaDict['pandas_profile_hash'] = hash

    if(fileExtension == '.dataset'):
        getDataset(event.src_path)

    if(event.is_directory):
        profileArgs = ' -s -e --pool_size 3 --title ' + profileTitle
    else:
        profileArgs = ' -s -m --title ' + profileTitle
    profilingCommand = 'pandas_profiling ' + event.src_path + ' ' + profilePath + profileArgs
    
    if(CLIexecSync(profilingCommand, display=False, debugInfo=False)):
        saveMetadata(metaPath, metaDict)
    