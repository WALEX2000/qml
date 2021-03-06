import sys
from os import path, makedirs
import shutil
import site
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

def addCustomPackages(projRoot: str):
    site_packages = ""
    for sys_path in sys.path:
        _, tail = path.split(sys_path)
        if(tail == "site-packages" and sys_path.startswith(projRoot)):
            site_packages = sys_path
            break
    if(site_packages == ""): return

    destFolder = site_packages + "/qml_custom/"
    makedirs(destFolder, exist_ok=True)
    open(destFolder+'__init__.py', 'a').close()

    data_handler_asset_path = getAssetPath('data_handler.py')
    data_handler_dest = destFolder + 'data_handler.py'
    shutil.copyfile(data_handler_asset_path, data_handler_dest)

    paths_assetPath = getAssetPath('path.pth')
    dest_paths_file = site_packages + '/path.pth'
    shutil.copyfile(paths_assetPath, dest_paths_file)

def runProcess(args : "list[str]"):
    projRoot = ProjectSettings.getProjPath()
    print('\n-> Installing Dependencies')
    installDependencies(projRoot)
    print('\n-> Add Custom Packages')
    addCustomPackages(projRoot)
    print('\n-> Initiating Git')
    initGit(projRoot)
    print('\n-> Initiating DVC')
    initDVC(projRoot)
    if '-t' in args:
        print('\n-> Adding Template Files')
        addTemplateDatasetToDVC(projRoot)
    print('\n-> Commiting setup to Git')
    gitCommit('Setup Project!', projRoot)