import string
import typer
import click
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import sys
import shutil
import io
from types import SimpleNamespace
from collections import namedtuple

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
    # Add Template files
    pipfile = os.path.dirname(os.path.abspath(__file__)) + "/Templates/Pipfile"
    shutil.copy(pipfile, rootPath)
    
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

def initGit(projRoot: string):
    CLIexec('git init', projRoot)
    CLIexec('git add *', projRoot)

def gitCommit(message: string, projRoot: string):
    cmd = 'git commit -m "' + message + '"'
    CLIexec(cmd, projRoot)

@click.command()
@click.option('-n', '--name', type=str, help='Name of root project directory', default='Root_of_Project')
def setup(name):
    print("Commencing Setup...")
    print('\n-> Creating Project Structure')
    paths = setupProjectStructure(name)
    # -- Initialize git --
    print('\n-> Installing Dependencies')
    installDependencies(paths.rootPath)
    print('\n-> Initiating Git')
    initGit(paths.rootPath)
    print('\n-> Initiating DVC')
    initDVC(paths.rootPath)
    print('\n-> Commiting setup to Git')
    gitCommit('Setup Project!', paths.rootPath)
    print("\n...Setup Complete!")

@click.command()
def stuff():
    print(setupProjectStructure("oioi"))


app = typer.Typer()
@app.callback()
def callback():
    """
    Necessary for Typer to work with Clicker
    """

typer_click_object = typer.main.get_command(app)
typer_click_object.add_command(setup, "setup")
typer_click_object.add_command(stuff, "stuff")

@app.command()
def cli():
    typer_click_object()

if __name__ == "__main__":
    typer_click_object()