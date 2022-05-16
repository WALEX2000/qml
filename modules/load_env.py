import time
from modules.general_utils import getYAML, runProcesses, ProjectSettings, getAssetPath, getEnvConfigPath, LOCAL_CONFIG_FILE_NAME, storeYAML
from modules.watchdog_manager import launchWatchDogs, stopWatchDogs
import os
import shutil
import venv
import site
import sys

def dictToDir(data : dict, path : str = ""):
    """dictToDir expects data to be a dictionary with one top-level key."""

    dest = os.path.join(os.getcwd(), path)

    if isinstance(data, dict):
        for k, v in data.items():
            os.makedirs(os.path.join(dest, k), exist_ok=True)
            dictToDir(v, os.path.join(path, str(k)))

    elif isinstance(data, list):
        for i in data:
            if isinstance(i, dict):
                dictToDir(i, path)
            else:
                try:
                    assetPath = getAssetPath(i)
                    if(os.path.exists(assetPath)): continue
                    print("Adding: " + assetPath)
                    shutil.copy(assetPath, dest)
                except:
                    print("WARNING: Couldn't add '" + i + "' to the project..")

    if isinstance(data, dict):
        return list(data.keys())[0]

def checkEnv(envFilePath : str, projPath : str) -> dict:
    """ Checks if the given environment file path correspondents to an existing qml configuration file, and starts ProjectSettings """
    envDict = getYAML(envFilePath)
    if(envDict is None):
        print("Couldn't read contents from .qml_env.yaml file")
        raise Exception("Couldn't start qml!")
    envName = envDict.get('name')
    if envName is None:
        print("Couldn't read name from .qml_env.yaml file")
        raise Exception("Couldn't start qml!")
    envVersion = envDict.get('version')
    if envVersion is None:
        print("Couldn't read version from .qml_env.yaml file")
        raise Exception("Couldn't start qml!")
    
    # Get the conf file and check the version (if they match, keep going, else give error)
    envConfPath = getEnvConfigPath(envName)
    if(not os.path.exists(envConfPath)):
        print(f"Couldn't find configuration file with name '{envName}' in qml resources")
        raise Exception("Couldn't start qml!")
    envConfDict = getYAML(envConfPath)
    if(envConfDict is None):
        print(f"Couldn't read contents from '{envConfPath}'")
        raise Exception("Couldn't start qml!")
    envConfVersion = envConfDict.get('version')
    if envConfVersion is None:
        print(f"Couldn't read version from '{envConfPath}'")
        raise Exception("Couldn't start qml!")
    if envConfVersion != envVersion:
        print(f"Version in given '.qml_env.yaml' file is different from the existing version in '{envConfPath}'")
        raise Exception("Couldn't start qml!")

    ProjectSettings(projPath, envName)
    return envConfDict

def loadEnv(envDict : dict, projPath : str) -> dict:
    print('-> Checking Project Structure')
    setupDict = envDict.get('setup')
    folderStructure = setupDict.get('structure')
    dictToDir(folderStructure, projPath)

    print('-> Starting Virtual Environemnt')
    _, projName = os.path.split(projPath)
    venvPath = projPath + "/.venv"
    venv.create(venvPath, system_site_packages=True, with_pip=True, prompt=projName)

    activate_this_file = venvPath + "/bin/activate_this.py"
    if(not os.path.exists(activate_this_file)):
        activateAssetPath = getAssetPath("activate_this.py")
        shutil.copyfile(activateAssetPath, activate_this_file)
    with open(activate_this_file) as f:
        code = compile(f.read(), activate_this_file, 'exec')
        exec(code, dict(__file__=activate_this_file))

    print('-> Running Setup Processes')
    setupProcesses : list[str] = setupDict.get('processes')
    runProcesses(setupProcesses)

    print('-> Starting Watchdog')
    dirList = envDict.get('watchdog')
    if dirList is not None:
        launchWatchDogs(dirList)

    print('-> Switch terminal shell')
    os.chdir(projPath)
    time.sleep(1)
    activateVenv = '/bin/bash --rcfile ' + projPath + '/.venv/bin/activate'
    os.system(activateVenv)
    
    print("\nClosed qml")
    if dirList is not None:
        stopWatchDogs()

def createEnv(envConfPath : str, projPath : str):
    """ gets the existing qml configuration and creates the .qml_env.yaml file in the appropriate place """
    print('..Loading Environment Configuration File')
    envDict = getYAML(envConfPath)
    if(envDict is None):
        print("Couldn't load configuration from environment file..")
        raise Exception("Couldn't start qml!")
    envVersion = envDict.get('version')
    if(envVersion is None):
        print("ERROR: Provided configuration file '" + envConfPath + "' does not contain a 'version' property")
        raise Exception("Couldn't start qml!")
    (_, envName) = os.path.split(envConfPath)
    
    envFilePath = projPath + '/' + LOCAL_CONFIG_FILE_NAME
    envFileDict = {
        "name":  envName,
        "version": envVersion
    }
    storeYAML(envFilePath, envFileDict)
