from modules.general_utils import CLIexecSync
from qml_environments.default_env.modules.inspect_data import getInfoFromDataPath, getMetadata, saveMetadata, metaInfoTemplate, hashFile
from os import path

def runEvent(event):
    if(event.is_directory is True): return
    (dataFileName, profilePath, profileTitle, fileExtension, metaPath) = getInfoFromDataPath(event.src_path)
    if(fileExtension == '.tmp' or dataFileName == '.DS_Store' or dataFileName == '.gitignore'): return

    hash = hashFile(event.src_path)
    metaDict = getMetadata(metaPath)
    if(metaDict is None): return # Only generate profile for tracked files
    elif(metaDict.get('pandas_profile_hash') == hash and path.exists(profilePath)): return
    metaDict['pandas_profile_hash'] = hash

    if(event.is_directory):
        profileArgs = ' -s -e --pool_size 3 --title ' + profileTitle
    else:
        profileArgs = ' -s -m --title ' + profileTitle
    profilingCommand = 'pandas_profiling ' + event.src_path + ' ' + profilePath + profileArgs
    
    if(CLIexecSync(profilingCommand, display=False, debugInfo=False)):
        saveMetadata(metaPath, metaDict)
    