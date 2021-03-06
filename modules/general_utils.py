from subprocess import CalledProcessError, CompletedProcess, Popen, PIPE, STDOUT, TimeoutExpired, run
import io
import os
import yaml
import importlib
from pathlib import Path
import sys
import site

LOCAL_CONFIG_FILE_NAME = '.qml_env.yaml'
DEFAULT_ENV = 'default_env'

def activateVenv():
    base = ProjectSettings.getProjPath() + "/.venv"
    bin_dir = base + "/bin"
    os.environ["PATH"] = os.pathsep.join([bin_dir] + os.environ.get("PATH", "").split(os.pathsep))
    os.environ["VIRTUAL_ENV"] = base  # virtual env is right above bin directory

    prev_length = len(sys.path)
    libDir = base + "/lib"
    for file in os.listdir(libDir):
        pkg_dir = os.path.join(libDir, file)
        if not os.path.isdir(pkg_dir): continue
        pkg_dir += "/site-packages"
        if(not os.path.exists(pkg_dir)): continue
        for lib in pkg_dir.split(os.pathsep):
            path = os.path.realpath(os.path.join(bin_dir, lib))
            site.addsitedir(path.decode("utf-8") if "" else path)
    site.addsitedir(ProjectSettings.getProjPath())
    
    sys.path[:] = sys.path[prev_length:] + sys.path[0:prev_length]
    sys.real_prefix = sys.prefix
    sys.prefix = base

def getEnvironmentResourcesPath() -> str:
    envName = ProjectSettings.getEnvName()
    parentDir = Path(__file__).parents[1]
    return str(parentDir) + f"/qml_environments/{envName}/"

def getAssetPath(fileName : str) -> str:
    """ Returns the path of an asset to be used inside the project """
    envRes = getEnvironmentResourcesPath()
    assetPath = envRes + "assets/" + fileName
    return assetPath

def getModulePakage():
    envName = ProjectSettings.getEnvName()
    return 'qml_environments.' + envName + '.modules.'

def getEnvConfigPath(envName : str) -> str:
    """ Returns the path of the specified env name """
    parentDir = Path(__file__).parents[1]
    envPath = str(parentDir) + "/qml_environments/" + envName + "/.env.yaml"
    return envPath

def CLIexecSync(cmd: str, execDir: str = os.getcwd(), display : bool = True, debugInfo : bool = True) -> bool:
    """Executes a CLI call and then returns True or False depedning on the success of the Call"""
    try:
        completedProcess : CompletedProcess = run(cmd, stdout = PIPE, stderr = PIPE, shell = True, cwd=execDir, check=True)
    except CalledProcessError as err:
        if(debugInfo):
            print(err.stderr.decode('utf-8'))
        return False
    
    if(display):
        print(completedProcess.stdout.decode('utf-8'))
    
    return True
    

def CLIexec(cmd: str, execDir: str = os.getcwd(), display : bool = True, debugInfo : bool = True):
    """Async CLI call, with optional real-time display of output and errors"""
    if(debugInfo): stderrOutput = STDOUT
    else: stderrOutput = None
    p = Popen(cmd, stdout = PIPE, stderr = stderrOutput, shell = True, cwd=execDir)
    if(not display): return True # If no Display, assume a correct execution of the process
    reader = io.TextIOWrapper(p.stdout, encoding=None, newline='')
    while not p.stdout.closed:
        char = reader.read(1)
        if(char == ''):
            break
        print(char, end='')
    reader.close()

    try:
        result = p.wait(timeout=3)
        if(result == 0): return True
        else: print('Process Call "' + cmd + '" Failed..')
    except TimeoutExpired as timeout:
        print('WARNING: Timed out while waiting for process "' + cmd + '". Will mark process as Failed')
    
    return False

def CLIcomm(cmd: str, execDir: str, inputs: "list[str]"):
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
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    with open(filePath, 'w') as file:
        yaml.dump(dict, file)

def runProcesses(processes : "list[str]", extraArgs : "list[str]"):
    modulePackage = getModulePakage()
    for process in processes:
        module = importlib.import_module(modulePackage + process)
        try:
            module.runProcess(extraArgs)
        except Exception as exc:
            print("\nERROR: Caught exception running setup process: '" + process + "'")
            print(exc)

def runEvents(processes : "list[str]", event):
    modulePackage = getModulePakage()
    for process in processes:
        module = importlib.import_module(modulePackage + process)
        try:
            module.runEvent(event)
        except Exception as exception:
            print("\nERROR: Caught exception running event: " + str(event) + "\n- The exception occurred in process: '" + process + "'")
            print(exception)

class ProjectSettings:
    __instance = None
    @staticmethod 
    def getProjPath():
        if ProjectSettings.__instance == None:
            raise Exception("Project Settings has not been initialized")
        return ProjectSettings.__instance.projPath

    @staticmethod 
    def getEnvName():
        if ProjectSettings.__instance == None:
            raise Exception("Project Settings has not been initialized")
        return ProjectSettings.__instance.envName

    @staticmethod 
    def getPythonVersion():
        if ProjectSettings.__instance == None:
            raise Exception("Project Settings has not been initialized")
        return ProjectSettings.__instance.pythonVersion
    
    def __init__(self, projPath, envName, pythonVersion):
        if ProjectSettings.__instance != None:
            return
        else:
            self.projPath = projPath
            self.envName = envName
            self.pythonVersion = pythonVersion
            ProjectSettings.__instance = self