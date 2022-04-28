from modules.general_utils import getYAML

def loadEnv(envName):
    envDict = getYAML(envName)
    setupDict = envDict.get('setup')
    print('Name: ' + str(envDict.get('name')))
    print('Setup: ' + str(setupDict))
    print('Structure: ' + str(setupDict.get('structure')))
