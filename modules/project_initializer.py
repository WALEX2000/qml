import string
import os
from subprocess import Popen, PIPE, STDOUT
import shutil
import io
from collections import namedtuple
from pathlib import Path

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
    mlPrimitivesPath = os.path.join(srcPath, 'ml_primitives')
    pipelinesPath = os.path.join(srcPath, 'pipelines')
    # Create Folders
    os.mkdir(rootPath, mode)
    os.mkdir(dataPath, mode)
    os.mkdir(srcPath, mode)
    os.mkdir(mlPrimitivesPath, mode)
    os.mkdir(pipelinesPath, mode)
    # Add Pipfiles
    pipfile = getTemplateFilePath('Pipfile')
    shutil.copy(pipfile, rootPath)
    pipfileLock = getTemplateFilePath('Pipfile.lock')
    shutil.copy(pipfileLock, rootPath)
    
    Paths = namedtuple('Paths', ['rootPath', 'dataPath', 'srcPath', 'mlPrimitivesPath', 'pipelinesPath'])
    return Paths(rootPath, dataPath, srcPath, mlPrimitivesPath, pipelinesPath)

def CLIexec(cmd: string, execDir: string):
    p = Popen(cmd, stdout = PIPE, stderr = STDOUT, shell = True, cwd=execDir)
    reader = io.TextIOWrapper(p.stdout, encoding=None, newline='')
    while not p.stdout.closed:
        char = reader.read(1)
        if(char == ''):
            break
        print(char, end='')

def installDependencies(projRoot: string):
    # Install dependencies with Pipenv
    CLIexec('pipenv install', projRoot)

def initDVC(projRoot: string):
    CLIexec('dvc init', projRoot)
    CLIexec('dvc config core.autostage true', projRoot)

def initGit(projRoot: string):
    CLIexec('git init', projRoot)

def gitCommit(message: string, projRoot: string):
    CLIexec('git add *', projRoot)
    cmd = 'git commit -m "' + message + '"'
    CLIexec(cmd, projRoot)

def addTemplateFiles(dataPath: string, rootPath: string):
    dataFile = getTemplateFilePath('winequality-red.csv')
    shutil.copy(dataFile, dataPath)
    dataFileReport = getTemplateFilePath('winequality-red.csv.pp')
    shutil.copy(dataFileReport, dataPath)
    CLIexec('dvc add data/winequality-red.csv', rootPath)

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
    print('\n-> Adding Template Files')
    addTemplateFiles(paths.dataPath, paths.rootPath)
    print('\n-> Commiting setup to Git')
    gitCommit('Setup Project!', paths.rootPath)
    print("\n...Setup Complete!")