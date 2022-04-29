import typer
import click
import os
from modules import example_module
from modules import data_inspector
from modules import project_initializer
from modules import auto_data_manager
from modules.load_env import loadEnv
import time

@click.command()
@click.option('-n', '--name', type=str, help='Name of root project directory', default=None)
@click.option('-env', type=str, help='Name of environment configuration file', default='qml-env.yaml')
def start(name, env):
    envPath = os.getcwd() + '/' + env
    rootPath = os.getcwd()
    load = True
    if(name is None and os.path.exists(envPath)):
        load = False
    else:
        rootPath += '/' + name
        load = not os.path.exists(rootPath)
    
    if(load):
        if(loadEnv('qml_assets/' + env, rootPath) is None): return
    
    dataPath = rootPath + '/data'
    auto_data_manager.watchData(dataPath, rootPath)
    os.chdir(rootPath)
    time.sleep(1)
    print("\nStarted qml")
    activateVenv = '/bin/bash --rcfile ' + rootPath + '/.venv/bin/activate'
    os.system(activateVenv)
    auto_data_manager.stopWatch()
    print("Closed qml")

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--checkpoint', '-ch', is_flag=True, help='Generate a Great Expectations checkpoint for this dataset')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def inspect_data(filename, checkpoint, args):
    parsedArgs = ' ' + ' '.join(args)
    data_inspector.inspectData(filename, parsedArgs)

@click.command()
def stuff():
    loadEnv("./Templates/qml-env.yaml")

app = typer.Typer()
@app.callback()
def callback():
    """
    Necessary for Typer to work with Clicker
    """

typer_click_object = typer.main.get_command(app)
typer_click_object.add_command(start, "start")
typer_click_object.add_command(stuff, "stuff")
typer_click_object.add_command(inspect_data, "inspect-data")

@app.command()
def cli():
    typer_click_object()

if __name__ == "__main__":
    typer_click_object()