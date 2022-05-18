import click
import nbformat.v4 as nbf
from nbformat import write as nbfWrite
from modules.general_utils import ProjectSettings
from os import path

NB_PATH = ProjectSettings.getProjPath() + '/src/data_analysis/'

# TODO install autoviz beforehand
# TODO If file already exists, create a new one
# TODO add option for .dataset load

@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--features', '-f', type=int, help='Number of features to automatically analyse', default=5)
def runCommand(filename, features):
    """ Create a jupyter notebook file with AutoViz inspecting features in dataset 'filename' and add to meta of filename """
    absFilePath = path.abspath(filename) # TODO Replace absolute with a relative path that works from the place the file is
    (_, filePathTail) = path.split(filename) # Head is path info, tail is name info
    datasetName, _ = path.splitext(filePathTail)

    notebook = nbf.new_notebook()
    text = f"""\
# {filePathTail} Explorative Data Analysis"""

    importCode = """\
from autoviz.AutoViz_Class import AutoViz_Class
%matplotlib inline
import pandas as pd"""

    setupCode = f"""\
dataFile = '{absFilePath}'
targetVar = '<INSERT NAME OF TARGET VARIABLE>' # Provide Target variable in case it is not specified
numAnalyzedCols = {features}"""
    
    pandasCode = f"""\
df = pd.read_csv(dataFile)
df.head()"""

    EDACode = """\
AV = AutoViz_Class()
dft = AV.AutoViz(
    filename=dataFile,
    sep=",",
    depVar=targetVar,
    dfte=None,
    header=0,
    verbose=1,
    lowess=False,
    chart_format="bokeh",
    max_rows_analyzed=100000,
    max_cols_analyzed=numAnalyzedCols
)"""

    notebook['cells'] = [nbf.new_markdown_cell(text),
    nbf.new_code_cell(importCode), nbf.new_code_cell(setupCode), nbf.new_code_cell(pandasCode), nbf.new_code_cell(EDACode)]

    nbFilePath = NB_PATH + datasetName + '_analysis.ipynb'
    with open(nbFilePath, 'w') as f:
        nbfWrite(notebook, f)
    
    print('Generated File: ' + nbFilePath)