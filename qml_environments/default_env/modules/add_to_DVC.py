import os
from modules.general_utils import ProjectSettings, CLIexecSync
from modules.default_env_modules.inspect_data import metaInfoTemplate, hashFile, saveMetadata

def runEvent(event):
    rootPath = ProjectSettings.getProjPath()
    dataConfPath = rootPath + '/data/data_conf/' # TODO Change path to accomodate data and models

    (_, filename) = os.path.split(event.src_path)
    if(filename.endswith('.tmp') or filename.endswith('.DS_Store')):
        return # Ignore .tmp files and .DS_Store files

    dvcFilePath = dataConfPath + filename + '.dvc'
    if(os.path.exists(dvcFilePath)):
        return # File is already being tracked, but .dvc may trigger creation twice, so don't do anything
    
    command = 'dvc add ' + event.src_path + ' --file ' + dvcFilePath
    CLIexecSync(command, rootPath, display=False)

    metaInfo = metaInfoTemplate.copy()
    metaInfo['type'] = "Data" # TODO Determine based on what is being submited in the event path
    metaInfo['version'] = '.0' # TODO Change according to how it should be changed
    saveMetadata(dvcFilePath, metaInfo)