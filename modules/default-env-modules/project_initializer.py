import os
import shutil
from collections import namedtuple
from pathlib import Path
from modules.general_utils import CLIexec, CLIcomm, ProjectSettings

def installDependencies(projRoot: str):
    os.environ['PIPENV_VENV_IN_PROJECT'] = "enabled"
    CLIexec('pipenv install', projRoot)

def initDVC(projRoot: str):
    CLIexec('dvc init', projRoot)
    CLIexec('dvc config core.autostage true', projRoot)

def initGit(projRoot: str):
    CLIexec('git init', projRoot)

def gitCommit(message: str, projRoot: str):
    CLIexec('git add *', projRoot)
    cmd = 'git commit -m "' + message + '"'
    CLIexec(cmd, projRoot)

def addTemplateDatasetToDVC(rootPath: str):
    CLIexec('dvc add data/winequality-red.csv --file data/data_conf/winequality-red.csv.dvc', rootPath)

def initGreatExpectations(projRoot: str):
    CLIcomm('great_expectations init', projRoot, ["y", "banana"])

def runProcess():
    projRoot = ProjectSettings.getProjPath()
    print('\n-> Installing Dependencies')
    installDependencies(projRoot)
    print('\n-> Initiating Git')
    initGit(projRoot)
    print('\n-> Initiating DVC')
    initDVC(projRoot)
    print('\n-> Initiating Great Expectations')
    initGreatExpectations(projRoot)
    print('\n-> Adding Template Files')
    addTemplateDatasetToDVC(projRoot)
    print('\n-> Commiting setup to Git')
    gitCommit('Setup Project!', projRoot)