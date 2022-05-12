from modules.general_utils import CLIexecSync
from modules.default_env_modules.inspect_data import getInfoFromDataPath, getMetadata, saveMetadata, metaInfoTemplate, hashFile
from os import path

def runEvent(event):
    (_, profilePath, profileTitle, fileExtension, metaPath) = getInfoFromDataPath(event.src_path)
    if(fileExtension == '.tmp'): return

    hash = hashFile(event.src_path)
    metaDict = getMetadata(metaPath)
    if(metaDict is None): metaDict = metaInfoTemplate
    elif(metaDict.get('pandas_profile_hash') == hash and path.exists(profilePath)): return
    metaDict['pandas_profile_hash'] = hash

    if(fileExtension == '.dataset'):
        # Might need temporary files for .dataset file (Created temporary dataframe maybe? and then inspect it with pandas profile)
        pass

    if(event.is_directory):
        profileArgs = ' -s -e --pool_size 3 --title ' + profileTitle
    else:
        profileArgs = ' -s -m --title ' + profileTitle
    profilingCommand = 'pandas_profiling ' + event.src_path + ' ' + profilePath + profileArgs
    
    if(CLIexecSync(profilingCommand, display=False, debugInfo=False)):
        saveMetadata(metaPath, metaDict)
    