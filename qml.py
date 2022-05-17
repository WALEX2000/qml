import click
import os
from modules.general_utils import getEnvConfigPath, getYAML, LOCAL_CONFIG_FILE_NAME
from modules.load_env import createEnv, checkEnv, loadEnv
import importlib
from pathlib import Path
import sys

@click.group()
def cli():
    pass

def addCommandsToQml(projRootPath : str, envConfDict : dict):
    envName = envConfDict.get('name')
    if envName is None: return
    simpleName, _ = os.path.splitext(envName)
    simpleName = simpleName[1:]

    # Activate Python virtualenv
    venvPath = projRootPath + "/.venv"
    activate_this_file = venvPath + "/bin/activate_this.py"
    if(not os.path.exists(activate_this_file)):
        return
    with open(activate_this_file) as f:
        code = compile(f.read(), activate_this_file, 'exec')
        exec(code, dict(__file__=activate_this_file))

    envFilePath = projRootPath + "/" + LOCAL_CONFIG_FILE_NAME
    try:
        envDict = checkEnv(envFilePath, projRootPath)
    except:
        return

    modulePackage = 'modules.' + simpleName + '_modules.'
    def bindCommand(commandName):
        try:
            module = importlib.import_module(modulePackage + commandName)
        except ModuleNotFoundError:
            return None

        func = module.runCommand
        func.__name__ = commandName
        return func

    commands : list[str] = envDict.get('commands')
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

virtualEnvironment = os.environ.get('VIRTUAL_ENV')
tail = None
if virtualEnvironment is not None:
    head, tail = os.path.split(os.environ.get('VIRTUAL_ENV'))
if tail == '.venv': # running inside what is possibly a qml environment
    envConfLocation = head + '/' + LOCAL_CONFIG_FILE_NAME
    envConfDict = getYAML(envConfLocation)
    if envConfDict is not None: # If we were able to read a env YAML file from the location of the .venv, then we can proceed
        addCommandsToQml(os.getcwd(), envConfDict)

@cli.command()
@click.option('-p', '--path', type=str, help='Name of root project directory relative to current directory', default=None)
@click.option('-conf', '--config', type=str, help='Name of configuration file for setup of a new environment', default=None)
def start(path, config):
    if path is None: rootPath = os.getcwd()
    else: rootPath = os.getcwd() + '/' + path
    localConfigPath = rootPath + '/' + LOCAL_CONFIG_FILE_NAME

    if config is None: # No config was specified (either create new, or boot up)
        if(os.path.exists(localConfigPath)):
            print('Environment Configuration Detected!')
            configAssetPath = localConfigPath
            setup = False # Pre-existing environment has already been setup
        else:
            configAssetPath = getEnvConfigPath('.default_env.yaml')
            setup = True  # There's no Pre-existing environemnt
    else: # A config was specified (create new)
        setup = True
        configFileName = '.' + config + '.yaml'
        configAssetPath = getEnvConfigPath(configFileName)
        if (not os.path.exists(configAssetPath)):
            print('ERROR: Specified configuration file ' + config + ' could not be found in package assets')
            return
        
        if(os.path.exists(localConfigPath)): # An environment has alread been setup before
            print("ERROR: provided a configuration file: '" + config + "' But there already exists one in this directory: '" + localConfigPath + "'")
            return
    
    if(setup):  # Need to create new Env
        print('No existing environemnt found. Will start a new one..')
        createEnv(configAssetPath, rootPath)
    
    envDict = checkEnv(localConfigPath, rootPath)
    loadEnv(envDict, rootPath)

@cli.command()
def edit():
    qmlDirectory = str(Path(__file__).parents[0])
    print(f'\nTo Create/Edit QML Environments, work in this directory: {qmlDirectory}\n')

if __name__ == "__main__":
    cli()