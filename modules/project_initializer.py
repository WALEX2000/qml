import os
import shutil
from collections import namedtuple
from pathlib import Path
from . import general_utils

Paths = namedtuple('Paths', ['rootPath', 'dataPath', 'srcPath', 'mlPrimitivesPath', 'pipelinesPath', 'dataConfPath'])

def getTemplateFilePath(fileName):
    parentDir = Path(__file__).parents[1]
    filePath = str(parentDir) + "/Templates/" + fileName
    return filePath

def setupProjectStructure(name):
    mode = 0o777
    # Create Paths
    rootPath = os.path.join(os.getcwd(), name)
    dataPath = os.path.join(rootPath, 'data')
    srcPath = os.path.join(rootPath, 'src')
    dataConfPath = os.path.join(dataPath, 'dataConf')
    mlPrimitivesPath = os.path.join(srcPath, 'ml_primitives')
    pipelinesPath = os.path.join(srcPath, 'pipelines')
    # Create Folders
    os.mkdir(rootPath, mode)
    os.mkdir(dataPath, mode)
    os.mkdir(dataConfPath, mode)
    os.mkdir(srcPath, mode)
    os.mkdir(mlPrimitivesPath, mode)
    os.mkdir(pipelinesPath, mode)
    # Add Pipfiles
    pipfile = getTemplateFilePath('Pipfile')
    shutil.copy(pipfile, rootPath)
    pipfileLock = getTemplateFilePath('Pipfile.lock')
    shutil.copy(pipfileLock, rootPath)
    
    return Paths(rootPath, dataPath, srcPath, mlPrimitivesPath, pipelinesPath, dataConfPath)

def installDependencies(projRoot: str):
    general_utils.CLIexec('export PIPENV_VENV_IN_PROJECT="enabled"')
    general_utils.CLIexec('pipenv install', projRoot)
    general_utils.CLIexec('unset PIPENV_VENV_IN_PROJECT')

def initDVC(projRoot: str):
    general_utils.CLIexec('dvc init', projRoot)
    general_utils.CLIexec('dvc config core.autostage true', projRoot)

def initGit(projRoot: str):
    general_utils.CLIexec('git init', projRoot)

def gitCommit(message: str, projRoot: str):
    general_utils.CLIexec('git add *', projRoot)
    cmd = 'git commit -m "' + message + '"'
    general_utils.CLIexec(cmd, projRoot)

def addTemplateFiles(dataPath: str, rootPath: str):
    dataFile = getTemplateFilePath('winequality-red.csv')
    shutil.copy(dataFile, dataPath)
    dataFileReport = getTemplateFilePath('winequality-red.csv.pp')
    shutil.copy(dataFileReport, dataPath)
    general_utils.CLIexec('dvc add data/winequality-red.csv -f data/dataConf/winequality-red.csv.dvc', rootPath)

def initGreatExpectations(projRoot: str):
    general_utils.CLIcomm('great_expectations init', projRoot, ["y", "banana"])

def setupProject(name):
    print("Commencing Setup...")
    print('\n-> Creating Project Structure')
    paths = setupProjectStructure(name)
    print('\n-> Installing Dependencies')
    installDependencies(paths.rootPath)
    print('\n-> Initiating Git')
    initGit(paths.rootPath)
    print('\n-> Initiating DVC')
    initDVC(paths.rootPath)
    print('\n-> Initiating Great Expectations')
    initGreatExpectations(paths.rootPath)
    print('\n-> Adding Template Files')
    addTemplateFiles(paths.dataPath, paths.rootPath)
    print('\n-> Commiting setup to Git')
    gitCommit('Setup Project!', paths.rootPath)
    print("\n...Setup Complete!")

    return paths