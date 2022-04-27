import os
import pandas as pd
import pathlib
import hashlib
from pandas_profiling import ProfileReport
import tempfile
from modules.cli_utils import CLIexec
import webbrowser
import great_expectations as ge
from great_expectations import DataContext
import ruamel.yaml

def checkIfValidDF(filename, fileExtension):
    df = pd.DataFrame()
    supportedFileTypes = ('.csv', '.json', '.pickle', '.pkl', '.parquet', '.fea', '.feather')

    # Check if it is a valid file (accepted by pandas)
    if(not fileExtension.endswith(supportedFileTypes)):
        print("ERROR: Unsupported file extension detected: '" + fileExtension + "'")
        print("These are the supported extensions:")
        print(supportedFileTypes)
        return False
    elif(fileExtension == '.csv'):
        df = pd.read_csv(filename)
    elif(fileExtension == '.json'):
        df = pd.read_json(filename, typ='frame')
    elif(fileExtension == '.pickle' or fileExtension == '.pkl'):
        df = pd.read_pickle(filename)
    elif(fileExtension == '.parquet'):
        df = pd.read_parquet(filename)
    elif(fileExtension == '.fea' or fileExtension == '.feather'):
        df = pd.read_feather(filename)
    
    # Check if df has been properly instantiated
    if (not isinstance(df, pd.DataFrame)):
        print("ERROR: Couldn't read DataFrame from file '" + filename + "'")
        print("Please make  sure that '" + filename + "' contains a valid DataFrame")
        return False
    
    return df

def generateReportProfile(data, name):
    def handleUnknownErrors(e):
        print("An Unknown Error Occured:")
        print(e)

    profileName = name + " Dataset Report"
    profile = None
    try:
        profile = ProfileReport(data, title=profileName, minimal=True)
        profile.to_html()
    except IndexError:
        print("Full Profile can't be generated on this dataset due to an unknwon issue")
        print("Generating Min Profile instead")
        try:
            profile = ProfileReport(data, title=profileName, minimal=True)
            profile.to_html()
        except Exception as e:
            handleUnknownErrors(e) 
            return False   
    except Exception as e:
        handleUnknownErrors(e)
        return False

    """ TODO
    datasetName = "data"
    context: DataContext = ge.get_context()
    profile.to_expectation_suite(suite_name=datasetName+'_expSuite', data_context=context, build_data_docs=False, run_validation=False, save_suite=False)
    """
    return profile

def displayReport(profile: ProfileReport):
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        url = 'file://' + f.name
        f.write(profile.html)
    webbrowser.open(url)

def saveProfile(profile: ProfileReport, filename):
    profileFilename = "./" + filename + ".pp"
    profile.dump(profileFilename)

def addMetadataToDVC(filename):
    dvcPath = filename + ".dvc"
    if(os.path.exists(dvcPath)):
        # TODO add path of profile to dvc meta information (Might be useful for extension)
        pass
    else:
        print("WARNING: The data file you are inspecting is not currently being tracked by DVC.\nPlease consider adding ti to DVC tracking.")

def hashFile(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""
   # make a hash object
   h = hashlib.sha1()
   # open file for reading in binary mode
   with open(filename,'rb') as file:
       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

def inspectData(filename, args):
    #Check if profiling report already exists
    #If it does exist, just display it
    #If it doesn't exist, generate and display it
    #If there are args, use them to generate a new report
        #After generating, save over the previous report, if there ever was one
    (filePathHead, filePathTail) = os.path.split(filename.lower())
    datasetName, fileExtension = os.path.splitext(filePathTail)
    profilePath = filePathHead + '/dataConf/' + datasetName + '-profile.html'
    profileTitle = "'" + filePathTail + " Profile Report'"

    profilingCommand = 'pandas_profiling ' + filename + ' ' + profilePath + ' -m --infer_dtypes --title ' + profileTitle
    CLIexec(profilingCommand)

    hash = hashFile(filename)

    

    # Save hash of file (without df) to either .dvc or .meta file
    # When doing inspect, if hashes match, simply display the existing .html
        # if hashes match, but no .html, regenerate .html
        # if hashes don't match, then regen
        # if args, then regen, regardless of hash (regen hash tho)

    # Then, do this automatically with the wathchdog thingie

    # Then, add great expectations support

    # Then, add Autoviz support

    """
    jsonTmpFile = tempfile.NamedTemporaryFile(suffix='.json')
    jsonContent = b''.join(jsonTmpFile.readlines())
    jsonTmpFile.close()
    jsonContent
    """

    """
    dataFrame = checkIfValidDF(filename, fileExtension)
    if(dataFrame is False): return
    
    pandasProfile = ProfileReport()
    generateProfile = True
    if(os.path.exists(profilePath)):
        pandasProfile.load(profilePath)
        dfProfile = ProfileReport(dataFrame)
        if(dfProfile.df_hash == pandasProfile.df_hash):
            generateProfile = False
            print("Pre-Generated Report Found! Rendering...")
    
    if(generateProfile):
        print("Starting Report Generation...")
        pandasProfile = generateReportProfile(dataFrame, datasetName)
        if(pandasProfile is False): return
        saveProfile(pandasProfile, filename)
        addMetadataToDVC(filename)

    displayReport(pandasProfile)
    """

