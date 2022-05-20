import click
from os import path
import nbformat.v4 as nbf
from nbformat import write as nbfWrite
from modules.general_utils import ProjectSettings

NB_PATH = ProjectSettings.getProjPath() + '/src/data_analysis/dataset_generators/'

@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
def runCommand(datapath):
    """ Generates a jupyter notebook that creates a handler for a raw data file, to be used in further ML operations"""
    (_, filePathTail) = path.split(datapath) # Head is path info, tail is name info
    dataName, _ = path.splitext(filePathTail)

    nbFilePath = NB_PATH + 'gen_' + dataName + '_handler.ipynb'
    if(path.exists(nbFilePath)):
        print(f"ERROR: The file you are trying to generate already exists: '{nbFilePath}'")
        return

    dataPathRelativeToGen = '../../../data/' + filePathTail
    handlerPathRelativeToGen = '../../../data/data_conf/' + filePathTail + '.handler'

    notebook = nbf.new_notebook()
    text = f"""\
# Data Handler Generator for {filePathTail} Raw Data File"""
    
    importCode = f"""\
from qml_custom.data_handler import DataHandler
from sklearn.metrics import accuracy_score"""

    handlerCreatorCode = f"""\
dataPath = '{dataPathRelativeToGen}'
targetVarName = '<Insert Name of Target Variable>'
scoringFunction = accuracy_score # Edit with more adequate scoring function if deemed necessary

dataHandler = DataHandler(targetVarName, scoringFunction, dataPath=dataPath)
dataHandler.getDataframe().head()"""

    saveHandlerCode = f"""\
# Do NOT edit the save path
savePath = '{handlerPathRelativeToGen}'
dataHandler.save(savePath)"""

    notebook['cells'] = [nbf.new_markdown_cell(text),
    nbf.new_code_cell(importCode), nbf.new_code_cell(handlerCreatorCode),
    nbf.new_code_cell(saveHandlerCode)]

    with open(nbFilePath, 'w') as f:
        nbfWrite(notebook, f)
    
    print('Handler Generator File Created Here: ' + nbFilePath)