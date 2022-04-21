import os
import pandas as pd
from pandas_profiling import ProfileReport
import tempfile
import webbrowser

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
        profile = ProfileReport(data, title=profileName, explorative=True)
        profile.to_html()
    except IndexError:
        print("Full Profile can't be generated on this dataset due to an unknwon cause")
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

    # profile.to_expectation_suite() # TODO
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

def inspectData(filename):
    filenameBody, fileExtension = os.path.splitext(filename.lower())
    profileFilename = "./" + filename + ".pp"
    dataFrame = checkIfValidDF(filename, fileExtension)
    if(dataFrame is False): return
    
    pandasProfile = ProfileReport()
    generateProfile = True
    if(os.path.exists(profileFilename)):
        pandasProfile.load(profileFilename)
        dfProfile = ProfileReport(dataFrame)
        if(dfProfile.df_hash == pandasProfile.df_hash):
            generateProfile = False
            print("Pre-Generated Report Found! Rendering...")
    
    if(generateProfile):
        print("Starting Report Generation...")
        pandasProfile = generateReportProfile(dataFrame, filenameBody)
        if(pandasProfile is False): return
        saveProfile(pandasProfile, filename)
        addMetadataToDVC(filename)

    displayReport(pandasProfile)

