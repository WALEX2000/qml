import os
import pandas as pd
from pandas_profiling import ProfileReport

def checkIfValidDF(filename):
    df = pd.DataFrame()
    fileBody, fileExtension = os.path.splitext(filename.lower())
    supportedFileTypes = ('.csv', '.json', '.pickle', '.pkl', '.parquet', '.fea', '.feather')

    # Check if saved profile already exists

    # Check if it is a valid file (accepted by pandas)
    if(not fileExtension.endswith(supportedFileTypes)):
        print("ERROR: Unsupported file extension detected: '" + fileExtension + "'")
        print("These are the supported extensions:")
        print(supportedFileTypes)
        return False
    elif(fileExtension == '.csv'):
        df = pd.read_csv(filename)
    elif(fileExtension == '.json'):
        df = pd.read_json(filename, typ='frame')
    elif(fileExtension == '.pickle' or fileExtension == '.pkl'):
        df = pd.read_pickle(filename)
    elif(fileExtension == '.parquet'):
        df = pd.read_parquet(filename)
    elif(fileExtension == '.fea' or fileExtension == '.feather'):
        df = pd.read_feather(filename)
    
    # Check if df has been properly instantiated
    if (not isinstance(df, pd.DataFrame)):
        print("ERROR: Couldn't read DataFrame from file '" + filename + "'")
        print("Please make  sure that '" + filename + "' contains a valid DataFrame")
        return False
    
    return df

def inspectData(filename):
    dataFrame = checkIfValidDF(filename)
    if(dataFrame is False): return
    elif(dataFrame is True):
        # Load profile from file
        pass

    # Check if there is a .dvc file
    # If dataset has been added on DVC I can add the path of the profile to the meta
    dvcPath = filename + ".dvc"
    if(not os.path.exists(dvcPath)):
        print("WARNING: The data file you are inspecting is not currently being tracked by DVC. Please consider adding ti to DVC tracking.")

    # Generate Report