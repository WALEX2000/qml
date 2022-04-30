import click
import os
from modules import example_module, watchdog
from modules import data_inspector
from modules.general_utils import getAssetPath, getYAML, LOCAL_CONFIG_FILE_NAME
from modules.load_env import loadEnv
import time

@click.group()
def cli():
    pass

# TODO I think this is executed before any qml call
# So, I think I might have to place the config file inside a fixed directory on the virtual environment
# Then, whenver I call qml, this here will check for the existence and validity of that file
# If it finds a valid file it'll add the commands to the tool
commands = ['more_commands_maybe']
def bind_function(name, c):
    def func():
        print("I am the '{}' command".format(c))

    func.__name__ = name
    return func

for c in commands:
    f = bind_function('_f', c)
    _f = cli.command(name=c)(f)

@cli.command()
@click.option('-p', '--path', type=str, help='Name of root project directory relative to current directory', default=None)
@click.option('-conf', '--config', type=str, help='Name of configuration file for setup of a new environment', default=None)
def start(path, config):
    if path is None: rootPath = os.getcwd()
    else: rootPath = os.getcwd() + '/' + path
    localConfigPath = rootPath + '/' + LOCAL_CONFIG_FILE_NAME

    if config is None:
        configAssetPath = getAssetPath(LOCAL_CONFIG_FILE_NAME)
        if(os.path.exists(localConfigPath)):
            print('Environment Configuration Detected!')
            setup = False # Pre-existing environment has already been setup
        else:
            setup = True  # There's no Pre-existing environemnt
    else:
        configFileName = '.' + config + '.yaml'
        configAssetPath = getAssetPath(configFileName)
        if (not os.path.exists(configAssetPath)):
            print('ERROR: Specified configuration file ' + config + ' could not be found in package assets')
            return
        
        if(os.path.exists(localConfigPath)): # An environment has alread been setup before
            localConfDict = getYAML(localConfigPath)
            if localConfDict is None: return
            envName = localConfDict.get('name')
            if envName is None:
                print("ERROR: Local configuration file '" + localConfigPath + "' doesn't contain required property 'name'")
                return
            if envName == config:
                print('Matching Environment Configuration Detected!')
                setup = False # confs match so we can just load existing one
            else:
                print("ERROR: provided configuration file '" + config + "' doesn't match existing configuration '" + localConfigPath + "'")
                return
        else:
            setup = True  # There's no Pre-existing environemnt
    
    if(setup):
        print('No existing environemnt found. Will start a new one..')
        envDict = loadEnv(configAssetPath, rootPath, True)
    else:
        envDict = loadEnv(localConfigPath, rootPath, False)
    if envDict is None: return

    dirList = envDict.get('watchdog')
    if dirList is not None:
        watchdog.launchWatchDogs(dirList)

    os.chdir(rootPath)
    time.sleep(1)
    print("\nStarted qml")
    activateVenv = '/bin/bash --rcfile ' + rootPath + '/.venv/bin/activate'
    os.system(activateVenv)

    if dirList is not None:
        watchdog.stopWatchDogs()
    
    print("\nClosed qml")

@cli.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--checkpoint', '-ch', is_flag=True, help='Generate a Great Expectations checkpoint for this dataset')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def inspect_data(filename, checkpoint, args):
    parsedArgs = ' ' + ' '.join(args)
    data_inspector.inspectData(filename, parsedArgs)

@cli.command()
def stuff():
    print("HEY!")

if __name__ == "__main__":
    cli()