import typer
import click
import os
from modules import example_module
from modules import data_inspector
from modules import project_initializer
from modules import auto_data_manager
import time

@click.command()
@click.option('-n', '--name', type=str, help='Name of root project directory', default='Root_of_Project')
def start(name):
    # If cwd or name is a qml env previously created, start the virtualenv and run the workers
    rootPath = os.getcwd() + '/' + name
    dataPath = rootPath + '/data'
    if(not os.path.exists(rootPath)):
        project_initializer.setupProject(name)
    
    auto_data_manager.watchData(dataPath, rootPath)
    os.chdir(rootPath)
    time.sleep(1)
    print("\nStarted qml")
    activateVenv = '/bin/bash --rcfile ' + rootPath + '/bin/activate'
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
    example_module.exampleModule()

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