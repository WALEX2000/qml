import click
from os import path
import nbformat.v4 as nbf
from nbformat import write as nbfWrite
from modules.general_utils import ProjectSettings

NB_PATH = ProjectSettings.getProjPath() + '/src/data_analysis/dataset_generators/'

# TODO protect against overriding existing files

@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
def runCommand(datapath):
    """ Generates a jupyter notebook that turns a raw data file into a valid dataset, to be used in further ML operations"""
    (filePathHead, filePathTail) = path.split(datapath) # Head is path info, tail is name info
    dataName, _ = path.splitext(filePathTail)

    dataPathRelativeToGen = '../../../data/' + filePathTail
    datasetPathRelativeToGen = '../../../data/' + dataName + '.dataset'

    notebook = nbf.new_notebook()
    text = f"""\
# Dataset Generator for {filePathTail} Raw Data File"""
    
    importCode = f"""\
import pandas as pd
import pickle
from sklearn.metrics import accuracy_score
from mlprimitives.datasets import Dataset"""

    readDataCode = f"""\
# Edit function call until an adequate dataframe is achieved
dataframe = pd.read_csv('{dataPathRelativeToGen}')
dataframe.head()"""

    datasetCreatorCode = f"""\
datasetName = '{dataName} Dataset'
datasetDescription = '<Insert Description>'
dataModality = '<Insert Data Modality>' # single_table | multi_table | text | image | graph
taskType = '<Insert Task Type>' # classification | regression
targetVarName = '<Insert Name of Target Variable>'
scoringFunction = accuracy_score # Edit with more adequate scoring function if deemed necessary

_inputData = dataframe.loc[:, dataframe.columns != targetVarName]
_targetData = dataframe.loc[:, dataframe.columns == targetVarName]
dataset = Dataset(name=datasetName, description=datasetDescription, data=_inputData, target=_targetData, score=scoringFunction, data_modality=dataModality, task_type=taskType)

print(dataset.target.head())
print(dataset.data.head())"""

    saveDatasetCode = f"""\
with open('{datasetPathRelativeToGen}', 'wb') as datasetFile:
    pickle.dump(dataset, datasetFile)"""

    notebook['cells'] = [nbf.new_markdown_cell(text),
    nbf.new_code_cell(importCode), nbf.new_code_cell(readDataCode),
    nbf.new_code_cell(datasetCreatorCode), nbf.new_code_cell(saveDatasetCode)]

    nbFilePath = NB_PATH + 'gen_' + dataName + '_dataset.ipynb'
    with open(nbFilePath, 'w') as f:
        nbfWrite(notebook, f)
    
    print('\nDataset Generator File Created Here: ' + nbFilePath)