import os
from modules.general_utils import ProjectSettings, CLIexec

def runEvent(event):
    rootPath = ProjectSettings.getProjPath()
    dataConfPath = rootPath + '/data/data_conf/'

    (_, filename) = os.path.split(event.src_path)
    if(filename.endswith('.tmp')):
        return # Ignore .tmp files

    dvcFilePath = dataConfPath + filename + '.dvc'
    if(os.path.exists(dvcFilePath)):
        return # File is already being tracked, but .dvc may trigger creation twice, so don't do anything
    
    command = 'dvc add ' + event.src_path + ' --file ' + dvcFilePath
    CLIexec(command, rootPath, False)
