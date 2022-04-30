from modules.general_utils import getYAML, runProcesses, ProjectSettings, getAssetPath, LOCAL_CONFIG_FILE_NAME
import os
import shutil

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

def loadEnv(envConfPath : str, projPath : str, setup : bool) -> dict:
    print('..Loading Environment Configuration File')
    envDict = getYAML(envConfPath)
    if(envDict is None):
        print("Couldn't load configuration from environment file..")
        return None
    else:
        envName = envDict.get('name')
        if(envName is None):
            print("ERROR: Provided configuration file '" + envConfPath + "' does not contain a 'name' property")
            return None
    
    if(not setup):
        ProjectSettings(projPath, envName)
        return envDict

    print("\nCommencing Setup...")
    ProjectSettings(projPath, envName)
    setupDict = envDict.get('setup')
    folderStructure = setupDict.get('structure')
    print('-> Generating Project Structure')
    dictToDir(folderStructure, projPath)
    
    envConfDest = shutil.copy(envConfPath, projPath) # Add environment file to directory
    newConfName = projPath + '/' + LOCAL_CONFIG_FILE_NAME
    os.rename(envConfDest, newConfName) # Rename it to retain proper name

    setupProcesses : list[str] = setupDict.get('processes')
    runProcesses(setupProcesses)
    
    print('\n...Setup Complete!')

    return envDict
