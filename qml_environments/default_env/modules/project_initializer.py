import os
import shutil
from modules.general_utils import CLIexec, CLIcomm, ProjectSettings, getAssetPath

def installDependencies(projRoot: str):
    CLIexec('pip install -r requirements.txt', projRoot)

def initDVC(projRoot: str):
    CLIexec('dvc init', projRoot)
    CLIexec('dvc config core.autostage true', projRoot)
    CLIexec('dvc config cache.type copy', projRoot)

def initGit(projRoot: str):
    CLIexec('git init', projRoot)

def gitCommit(message: str, projRoot: str):
    CLIexec('git add *', projRoot)
    cmd = 'git commit -m "' + message + '"'
    CLIexec(cmd, projRoot)

def addTemplateDatasetToDVC(rootPath: str):
    assetPath = getAssetPath('winequality-red.csv')
    dest = rootPath + '/data/winequality-red.csv'
    shutil.copyfile(assetPath, dest)
    CLIexec('dvc add data/winequality-red.csv --file data/data_conf/winequality-red.csv.dvc', rootPath)

def initGreatExpectations(projRoot: str):
    CLIcomm('great_expectations init', projRoot, ["y"])

def runProcess(args : "list[str]"):
    projRoot = ProjectSettings.getProjPath()
    print('\n-> Installing Dependencies')
    installDependencies(projRoot)
    print('\n-> Initiating Git')
    initGit(projRoot)
    print('\n-> Initiating DVC')
    initDVC(projRoot)
    print('\n-> Initiating Great Expectations')
    initGreatExpectations(projRoot)
    if '-t' in args:
        print('\n-> Adding Template Files')
        addTemplateDatasetToDVC(projRoot)
    print('\n-> Commiting setup to Git')
    gitCommit('Setup Project!', projRoot)