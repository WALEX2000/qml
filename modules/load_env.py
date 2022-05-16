from modules.general_utils import getYAML, runProcesses, ProjectSettings, getAssetPath, getEnvConfigPath, LOCAL_CONFIG_FILE_NAME, storeYAML
import os
import shutil
import venv

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

    return

    print('-> Running Setup Processes')
    setupProcesses : list[str] = setupDict.get('processes')
    runProcesses(setupProcesses)

    print('-> Starting Watchdog')
    
    print('\n...Setup Complete!')

    # With the confFile perform the necessary loading, in order for the environment to work
        # May need to create Venv, if it doesn't exist
        # Or just activate it
    # Boot up the watchdog inside the venv (make it so it stops when yoou quit the venv (or add a qml exit))
    pass

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
