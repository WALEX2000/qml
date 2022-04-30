from subprocess import Popen, PIPE, STDOUT
import io
import os
import yaml
import importlib
from pathlib import Path

LOCAL_CONFIG_FILE_NAME = '.qml-env.yaml'

def getAssetPath(fileName : str) -> str:
    """ Returns the path of an asset to be used inside the project """
    envName = ProjectSettings.getEnvName()
    assetsFolderName = "/qml_assets/" + envName + "-assets/" + fileName
    parentDir = Path(__file__).parents[1]
    filePath = str(parentDir) + assetsFolderName
    return filePath

def getEnvConfigPath(envFileName : str) -> str:
    """ Returns the path of the specified env name """
    parentDir = Path(__file__).parents[1]
    envPath = str(parentDir) + "/qml_assets/" + envFileName
    return envPath

def CLIexec(cmd: str, execDir: str = os.getcwd(), display : bool = True):
    p = Popen(cmd, stdout = PIPE, stderr = STDOUT, shell = True, cwd=execDir)
    if(not display): return
    reader = io.TextIOWrapper(p.stdout, encoding=None, newline='')
    while not p.stdout.closed:
        char = reader.read(1)
        if(char == ''):
            break
        print(char, end='')
    
    reader.close()

def CLIcomm(cmd: str, execDir: str, inputs: list[str]):
    p = Popen(cmd, stdout = PIPE, stderr = STDOUT, stdin=PIPE, shell = True, cwd=execDir)
    reader = io.TextIOWrapper(p.stdout, encoding=None, newline='')
    writer = io.TextIOWrapper(p.stdin, line_buffering=True, newline=None)
    iterator = 0
    while not p.stdout.closed and not p.stdin.closed:
        if(iterator < len(inputs)):
            res = writer.write(inputs[iterator] + '\n')
            if(res == len(inputs[iterator]) + 1):
                iterator += 1
        char = reader.read(1)
        if(char == ''):
            break
        else:
            print(char, end='')
    
    reader.close()
    writer.close()

def getYAML(filePath: str) -> dict:
    if(not os.path.exists(filePath)): return None
    with open(filePath, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print("An Unkexpected error occurred while loading the YAML file: " + filePath)
            return None

def storeYAML(filePath: str, dict: dict):
    mode = 'w'
    if(not os.path.exists(filePath)): mode = 'x'
    with open(filePath, mode) as file:
        yaml.dump(dict, file)

def runProcesses(processes : list[str]):
    envName = ProjectSettings.getEnvName()
    modulePackage = 'modules.' + envName + '-modules.'
    for process in processes:
        module = importlib.import_module(modulePackage + process)
        module.runProcess()

def runEvents(processes : list[str], event):
    envName = ProjectSettings.getEnvName()
    modulePackage = 'modules.' + envName + '-modules.'
    for process in processes:
        module = importlib.import_module(modulePackage + process)
        module.runEvent(event)

class ProjectSettings:
    __instance = None
    @staticmethod 
    def getProjPath():
        if ProjectSettings.__instance == None:
            ProjectSettings()
        return ProjectSettings.__instance.projPath

    @staticmethod 
    def getEnvName():
        if ProjectSettings.__instance == None:
            ProjectSettings()
        return ProjectSettings.__instance.envName
    
    def __init__(self, projPath, envName):
        if ProjectSettings.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.projPath = projPath
            self.envName = envName
            ProjectSettings.__instance = self