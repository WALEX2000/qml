import click
import os
from modules.watchdog_manager import launchWatchDogs, stopWatchDogs
from modules.general_utils import getEnvConfigPath, getYAML, LOCAL_CONFIG_FILE_NAME
from modules.load_env import loadEnv
import time
import importlib

@click.group()
def cli():
    pass

def addCommandsToQml(envConfDict : dict):
    envName = envConfDict.get('name')
    if envName is None: return
    modulePackage = 'modules.' + envName + '_modules.'

    def bindCommand(commandName):
        try:
            module = importlib.import_module(modulePackage + commandName)
        except ModuleNotFoundError:
            return None

        func = module.runCommand
        func.__name__ = commandName
        return func

    commands : list[str] = envConfDict.get('commands')
    if commands is None: return
    for c in commands:
        commandName = c.get('command_name')
        if commandName is None:
            print("WARNING: A command specified in the configuration file does not contain a 'command_name' property, and will be ignored")
            continue
        
        contextSettings = c.get('settings')
        f = bindCommand(commandName)
        if f is None: continue
        else: cli.command(name=commandName, context_settings=contextSettings)(f)

# TODO This lets the user make use of the commands whenever he's inside the root proj Directory
# But it'd be better to let him use them whenever he's on the virtualenv shell (so he has access to the commands in all directories of that shell)
envConfLocation = os.getcwd() + '/' + LOCAL_CONFIG_FILE_NAME
envConfDict = getYAML(envConfLocation)
if envConfDict is not None:
    addCommandsToQml(envConfDict)

@cli.command()
@click.option('-p', '--path', type=str, help='Name of root project directory relative to current directory', default=None)
@click.option('-conf', '--config', type=str, help='Name of configuration file for setup of a new environment', default=None)
def start(path, config):
    if path is None: rootPath = os.getcwd()
    else: rootPath = os.getcwd() + '/' + path
    localConfigPath = rootPath + '/' + LOCAL_CONFIG_FILE_NAME

    if config is None:
        if(os.path.exists(localConfigPath)):
            print('Environment Configuration Detected!')
            configAssetPath = localConfigPath
            setup = False # Pre-existing environment has already been setup
        else:
            configAssetPath = getEnvConfigPath('.default_env.yaml')
            setup = True  # There's no Pre-existing environemnt
    else:
        configFileName = '.' + config + '.yaml'
        configAssetPath = getEnvConfigPath(configFileName)
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
        launchWatchDogs(dirList)

    os.chdir(rootPath)
    time.sleep(1)
    print("\nStarted qml")
    activateVenv = '/bin/bash --rcfile ' + rootPath + '/.venv/bin/activate'
    os.system(activateVenv)

    if dirList is not None:
        stopWatchDogs()
    
    print("\nClosed qml")

@cli.command()
def stuff():
    print(dict(ignore_unknown_options=True))
    print('commands:')
    envConfLocation = os.getcwd() + '/' + LOCAL_CONFIG_FILE_NAME
    envConfDict = getYAML(envConfLocation)
    commands = envConfDict.get('commands')
    print(commands)

if __name__ == "__main__":
    cli()