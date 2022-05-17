import click
from os import path
import nbformat.v4 as nbf
from nbformat import write as nbfWrite
from modules.general_utils import ProjectSettings

NB_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/'

@click.argument('name', type=str)
def runCommand(name):
    """Create a notetbook that generates an ML Pipeline, with the given name"""

    notebook = nbf.new_notebook()
    text = f"""\
# ML Pipeline: {name}"""

    importCode = """\
import mlblocks
from mlblocks import MLPipeline
from pprint import pprint"""

    primitiveLookupCode = """\
mlblocks.find_primitives('') # Primitive Lookup function"""

    mlPipelineCode = """\
# List of Primitives in the Pipeline (Edit as needed)
primitives = [
    'mlprimitives.custom.feature_extraction.CategoricalEncoder',
    'xgboost.XGBClassifier',
]

# List of extra arguments to call each primitive with (Edit as needed)
init_params = {
    'mlprimitives.custom.feature_extraction.CategoricalEncoder' : {},
    'xgboost.XGBClassifier' : {}
}

outputs = {
    "X": "dataset_features",
    "y": "dataset_labels"
}

pipeline = MLPipeline(primitives=primitives, init_params=init_params, outputs=outputs)"""

    hyperparametersLookupCode = """\
# See Pipeline parameters
pprint(pipeline.get_hyperparameters())"""

    notebook['cells'] = [nbf.new_markdown_cell(text),
    nbf.new_code_cell(importCode), nbf.new_code_cell(primitiveLookupCode),
    nbf.new_code_cell(mlPipelineCode), nbf.new_code_cell(hyperparametersLookupCode)]

    nbFilePath = NB_PATH + name + '.ipynb'
    with open(nbFilePath, 'w') as f:
        nbfWrite(notebook, f)
    
    print('\nCreated ML Pipeline Generator in: ' + nbFilePath)