import os
import hashlib
import tempfile
from modules.general_utils import CLIexec, storeYAML, getYAML
import great_expectations as ge
from great_expectations import DataContext
import webbrowser

metaInfo = {
  "profile-hash": "",
}

def hashFile(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""
   h = hashlib.sha1()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           h.update(chunk)

   return h.hexdigest()

def addMetadataToDVC(filename):
    dvcPath = filename + ".dvc"
    if(os.path.exists(dvcPath)):
        # TODO add path of profile to dvc meta information (Might be useful for extension)
        pass
    else:
        print("WARNING: The data file you are inspecting is not currently being tracked by DVC.\nPlease consider adding ti to DVC tracking.")

def inspectData(filename: str, args: str = ' '):
    (filePathHead, filePathTail) = os.path.split(filename.lower()) # Head is path info, tail is name info
    datasetName, fileExtension = os.path.splitext(filePathTail)
    profilePath = filePathHead + '/dataConf/' + datasetName + '-profile.html'
    metaPath = filePathHead + '/dataConf/' + datasetName + '-qmlMeta.yaml'
    profileTitle = "'" + filePathTail + " Profile Report'"
    profilingCommand = 'pandas_profiling ' + filename + ' ' + profilePath + ' --title ' + profileTitle
    hash = hashFile(filename)
    # Check if file has meta information and get it if it exists
    datasetMeta = getYAML(metaPath)
    if(datasetMeta is None):
        print("Dataset meta information couldn't be found. Generating new meta information")
        datasetMeta = metaInfo

    if(len(args) == 1):
        profilingCommand += ' -m'
        if(datasetMeta['profile-hash'] != hash or not os.path.exists(profilePath)):
            print("Profile hash is outdated. Generating new profile report..")
            CLIexec(profilingCommand)
            datasetMeta['profile-hash'] = hash
        else:
            print("Profile found. Rendering HTML..")
            url='file://' + str(os.path.abspath(profilePath))
            webbrowser.open(url)
            return
    else:
        profilingCommand += args
        print("Custom arguments detected. Calling pandas-profiling CLI..")
        CLIexec(profilingCommand)
        datasetMeta['profile-hash'] = hash
    
    storeYAML(metaPath, datasetMeta)

    # Then, do this automatically with the wathchdog thingie

    # Then, add great expectations support

    # Then, add Autoviz support

    """
    jsonTmpFile = tempfile.NamedTemporaryFile(suffix='.json')
    jsonContent = b''.join(jsonTmpFile.readlines())
    jsonTmpFile.close()
    jsonContent
    """
