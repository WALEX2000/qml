from modules.general_utils import getYAML
import os
import importlib
from modules import example_module

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
                # TODO copy files to proper place instead of creating new ones
                with open(os.path.join(dest, i), "a"):
                    os.utime(os.path.join(dest, i), None)

    if isinstance(data, dict):
        return list(data.keys())[0]

def loadEnv(envName : str):
    envDict = getYAML(envName)

    envImports : list[str] = envDict.get('imports')
    for module in envImports:
        importlib.import_module('modules.' + module)

    setupDict = envDict.get('setup')
    folderStructure = setupDict.get('structure')
    dictToDir(folderStructure, "./experiments") #TODO change path from experiments to proper place

    setupProcesses : list[str] = setupDict.get('exec')
    for process in setupProcesses:
        eval(process + '()')
