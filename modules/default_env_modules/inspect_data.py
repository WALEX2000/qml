from os import  path
from hashlib import sha1
from modules.general_utils import CLIexec, storeYAML, getYAML
from webbrowser import open as openURL
import click

metaInfo = {
  "profile-hash": "",
}

def hashFile(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""
   h = sha1()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           h.update(chunk)

   return h.hexdigest()

def addMetadataToDVC(filename):
    dvcPath = filename + ".dvc"
    if(path.exists(dvcPath)):
        # TODO add path of profile to dvc meta information (Might be useful for extension)
        pass
    else:
        print("WARNING: The data file you are inspecting is not currently being tracked by DVC.\nPlease consider adding ti to DVC tracking.")

def inspectData(filename: str, args: str = ' '):
    (filePathHead, filePathTail) = path.split(filename.lower()) # Head is path info, tail is name info
    datasetName, fileExtension = path.splitext(filePathTail)
    profilePath = filePathHead + '/data_conf/' + datasetName + '-profile.html'
    metaPath = filePathHead + '/data_conf/' + datasetName + '-qmlMeta.yaml'
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
        if(datasetMeta['profile-hash'] != hash or not path.exists(profilePath)):
            print("Profile hash is outdated. Generating new profile report..")
            CLIexec(profilingCommand)
            datasetMeta['profile-hash'] = hash
        else:
            print("Profile found. Rendering HTML..")
            url='file://' + str(path.abspath(profilePath))
            openURL(url)
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

@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--checkpoint', '-ch', is_flag=True, help='Generate a Great Expectations checkpoint for this dataset')
@click.pass_context
def runCommand(ctx, filename, checkpoint):
    parsedArgs = ' ' + ' '.join(ctx.args)
    inspectData(filename, parsedArgs)