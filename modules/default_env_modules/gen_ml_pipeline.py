import click
from os import path
import nbformat.v4 as nbf
from nbformat import write as nbfWrite
from modules.general_utils import ProjectSettings

NB_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/'

@click.argument('dataPath', type=click.Path(exists=True, dir_okay=False))
def runCommand(dataPath):
    """Generate a Pipeline that starts with the specified data"""
    (filePathHead, filePathTail) = path.split(dataPath) # Head is path info, tail is name info
    datasetName, _ = path.splitext(filePathTail)

    notebook = nbf.new_notebook()
    text = f"""\
# ML Pipeline for {filePathTail} Dataset"""

    importCode = """\
from autoviz.AutoViz_Class import AutoViz_Class"""

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
    nbf.new_code_cell(importCode), nbf.new_code_cell(EDACode)]

    nbFilePath = NB_PATH + datasetName + '_analysis.ipynb'
    with open(nbFilePath, 'w') as f:
        nbfWrite(notebook, f)
    
    print(nbFilePath)