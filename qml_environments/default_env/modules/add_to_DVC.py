import os
from modules.general_utils import ProjectSettings, CLIexecSync
from qml_environments.default_env.modules.inspect_data import metaInfoTemplate, saveMetadata

def runEvent(event):
    rootPath = ProjectSettings.getProjPath()
    dataConfPath = rootPath + '/data/data_conf/' # TODO Change path to accomodate data and models

    (_, filename) = os.path.split(event.src_path)
    if(filename.endswith('.tmp') or filename.endswith('.DS_Store') or filename.endswith('.gitignore')):
        return # Ignore .tmp files and .DS_Store files and .gitignore files

    dvcFilePath = dataConfPath + filename + '.dvc'
    if(os.path.exists(dvcFilePath)):
        return # File is already being tracked, but .dvc may trigger creation twice, so don't do anything
    
    command = 'dvc add ' + event.src_path + ' --file ' + dvcFilePath
    CLIexecSync(command, rootPath, display=False)

    metaInfo = metaInfoTemplate.copy()
    saveMetadata(dvcFilePath, metaInfo)
