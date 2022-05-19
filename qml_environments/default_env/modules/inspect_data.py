from os import  path
from hashlib import md5
from modules.general_utils import CLIexec, storeYAML, getYAML
from webbrowser import open as openURL
import click

metaInfoTemplate = { 
    "pandas_profile_hash": "",
}

def hashFile(filename):
   """"This function returns the MD5 hash
   of the file passed into it"""
   h = md5()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           h.update(chunk)

   return h.hexdigest()

def saveMetadata(metaPath : str, metaDict : dict):
    """Saves provided Metadata to .dvc file. If no DVC file found, metadata is not stored"""
    if(path.exists(metaPath)):
        dvcDict = getYAML(metaPath)
        if(dvcDict is None): return
        dvcDict['meta'] = metaDict
        storeYAML(metaPath, dvcDict)

def getMetadata(metaPath):
    """Finds Metadata stored in .dvc file and returns it. If none can be found, returns None"""
    metaDict = None
    if(path.exists(metaPath)):
        dvcDict = getYAML(metaPath)
        if(dvcDict is not None):
            metaDict = dvcDict.get('meta')
    return metaDict

def getInfoFromDataPath(filePath : str):
    (filePathHead, filePathTail) = path.split(filePath) # Head is path info, tail is name info
    datasetName, fileExtension = path.splitext(filePathTail)
    profilePath = filePathHead + '/data_conf/' + filePathTail + '.html'
    metaPath = filePathHead + '/data_conf/' + filePathTail + '.dvc'
    profileTitle = "'" + filePathTail + " Profile Report'"
    return (datasetName, profilePath, profileTitle, fileExtension, metaPath)

def getProfileCmd(filePath : str, profilePath : str, profileTitle : str):
    return 'pandas_profiling ' + filePath + ' ' + profilePath + ' --title ' + profileTitle

def inspectData(filePath: str, args: str, large: bool = False):
    (_, profilePath, profileTitle, _, metaPath) = getInfoFromDataPath(filePath)
    profilingCommand = getProfileCmd(filePath, profilePath, profileTitle)
    if(not large): profilingCommand += ' -m'
    
    hash = hashFile(filePath)
    datasetMeta = getMetadata(metaPath)
    if(datasetMeta is None): newMeta = metaInfoTemplate.copy()
    else: newMeta = datasetMeta

    if(len(args) == 0 and not large): # If no arguments were provided
        if(newMeta['pandas_profile_hash'] != hash or not path.exists(profilePath)): #Outdated or non-existent
            print("Profile hash is outdated. Generating new profile report..")
        else:
            print("Profile found. Rendering HTML..")
            url='file://' + str(path.abspath(profilePath))
            openURL(url)
            return
    else: # Arguments were given
        profilingCommand += ' ' + args
        print("Custom arguments detected. Calling pandas-profiling CLI..")
    
    if(not CLIexec(profilingCommand)): # If call failed, return
        return
    elif(args.count('-h') == 0): # If call wasn't a mere help prompt
        newMeta['pandas_profile_hash'] = hash
        saveMetadata(metaPath, newMeta)

@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--full', '-f', is_flag=True, help='Generate the full report for the data-set. Default is minimal')
@click.pass_context
def runCommand(ctx, filename, full):
    parsedArgs = ' '.join(ctx.args)
    inspectData(filename, parsedArgs, full)