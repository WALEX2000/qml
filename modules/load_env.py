from modules.general_utils import getYAML, runProcesses, ProjectSettings
import os
import importlib
import shutil
from pathlib import Path

def getAssetPath(fileName):
    parentDir = Path(__file__).parents[1]
    filePath = str(parentDir) + "/qml_assets/" + fileName
    return filePath

def dictToDir(data : dict, path : str = ""):
    """dictToDir expects data to be a dictionary with one top-level key."""

    dest = os.path.join(os.getcwd(), path)

    if isinstance(data, dict):
        for k, v in data.items():
            os.makedirs(os.path.join(dest, k))
            dictToDir(v, os.path.join(path, str(k)))

    elif isinstance(data, list):
        for i in data:
            if isinstance(i, dict):
                dictToDir(i, path)
            else:
                try:
                    assetPath = getAssetPath(i)
                    shutil.copy(assetPath, dest)
                except:
                    print("ERROR: Couldn't add '" + i + "' to the project..")

    if isinstance(data, dict):
        return list(data.keys())[0]

def loadEnv(envName : str, projPath : str):
    print("Commencing Setup...")
    print('\n-> Loading Environment Configuration')
    envDict = getYAML(envName)
    if(envDict is None):
        print("Couldn't load configuration from specified environment file..")
        return None

    setupDict = envDict.get('setup')
    folderStructure = setupDict.get('structure')
    print('\n-> Generating Project Structure')
    dictToDir(folderStructure, projPath)
    
    assetPath = getAssetPath(envName)
    shutil.copy(assetPath, projPath)

    ProjectSettings(projPath)

    setupProcesses : list[str] = setupDict.get('run')
    runProcesses(setupProcesses)
    
    print('\n...Setup Complete!')

    return True
