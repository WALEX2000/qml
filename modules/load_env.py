from pathlib import Path
import time
from modules.general_utils import activateVenv, getYAML, runProcesses, ProjectSettings, getAssetPath, getEnvConfigPath, LOCAL_CONFIG_FILE_NAME, storeYAML
from modules.watchdog_manager import launchWatchDogs, stopWatchDogs
import os
import shutil
import venv
import sys
import re
import click


class ExtendedEnvBuilder(venv.EnvBuilder):
    """ This Builder makes it possible to assign a specific python path to the virtual environment """
    def __init__(self, *args, **kwargs):
        self.python = kwargs.pop('python')
        super().__init__(*args, **kwargs)
    
    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        executable = self.python
        dirname, exename = os.path.split(os.path.abspath(executable))
        context.executable = executable
        context.python_dir = dirname
        context.python_exe = exename
        return context


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
                    fullDest = dest + '/' + i
                    if(os.path.exists(fullDest)): continue
                    shutil.copy(assetPath, dest)
                except:
                    print("WARNING: Couldn't add '" + i + "' to the project..")

    if isinstance(data, dict):
        return list(data.keys())[0]

def checkValidPythonVersionFormat(pythonVersion : str) -> bool:
    if re.search("^\d(\.\d)*$", str(pythonVersion)): return True
    else: return False

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
    pythonVersion = envDict.get('python_version')
    if pythonVersion is not None and not checkValidPythonVersionFormat(pythonVersion):
        pythonVersion = None
        print(f"Warning: python_version is '{envFilePath}' does not contain a valid format, and will be ignored")
    
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

    ProjectSettings(projPath, envName, pythonVersion)
    return envConfDict

def loadEnv(envDict : dict, projPath : str, extraArgs : "list[str]") -> dict:
    print('-> Checking Project Structure')
    setupDict = envDict.get('setup')
    folderStructure = setupDict.get('structure')
    dictToDir(folderStructure, projPath)

    # Create Venv
    _, projName = os.path.split(projPath)
    venvPath = projPath + "/.venv"
    if(not os.path.exists(venvPath)):
        print('-> Creating Virtual Environemnt')
        pythonVersion = ProjectSettings.getPythonVersion()
        pythonPath = sys._base_executable
        if(pythonVersion is not None):
            print(f"This environment requires a specific python version: '{pythonVersion}'")
            pythonPath = click.prompt('Please insert the path to the appropriate python executable: ', type=click.Path(exists=True, dir_okay=False))

        builder = ExtendedEnvBuilder(system_site_packages=True, with_pip=True, prompt=projName, python=pythonPath)
        builder.create(venvPath)

    # Activate Venv
    activateVenv()

    print('-> Running Setup Processes')
    setupProcesses : list[str] = setupDict.get('processes')
    runProcesses(setupProcesses, extraArgs)

    print('-> Starting Watchdog')
    dirList = envDict.get('watchdog')
    if dirList is not None:
        launchWatchDogs(dirList)

    print('-> Switch terminal shell')
    os.chdir(projPath)
    time.sleep(1)
    switchShell = '/bin/bash --rcfile ' + projPath + '/.venv/bin/activate'
    os.system(switchShell)
    
    print("\nClosed qml")
    if dirList is not None:
        stopWatchDogs()

def createEnv(envConfPath : str, projPath : str, pythonVersion : str):
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
    _, envName = os.path.split(Path(envConfPath).parent)
    
    envFilePath = projPath + '/' + LOCAL_CONFIG_FILE_NAME
    envFileDict = {
        "name":  envName,
        "version": envVersion,
        "python_version": pythonVersion,
    }
    storeYAML(envFilePath, envFileDict)
