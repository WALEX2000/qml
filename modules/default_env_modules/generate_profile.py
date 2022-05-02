from modules.general_utils import CLIexec
from os import path

def runEvent(event):
    (_, filename) = path.split(event.src_path)
    if(filename.endswith('.tmp')):
        return # Ignore .tmp files

    (filePathHead, filePathTail) = path.split(filename.lower()) # Head is path info, tail is name info
    datasetName, fileExtension = path.splitext(filePathTail)
    profilePath = filePathHead + '/data_conf/' + datasetName + '-profile.html'
    profileTitle = "'" + filePathTail + " Profile Report'"

    if(event.is_directory):
        profileArgs = ' -s -e --pool_size 3 --title ' + profileTitle
    else:
        profileArgs = ' -s -m --title ' + profileTitle

    profilingCommand = 'pandas_profiling ' + event.src_path + ' ' + profilePath + profileArgs
    CLIexec(profilingCommand, display=True)
    