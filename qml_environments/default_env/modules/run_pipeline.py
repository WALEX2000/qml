import sys
import click
import mlblocks
from modules.general_utils import ProjectSettings
from os import path
from mlblocks import MLPipeline
from mlprimitives.datasets import Dataset
import pickle

PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/pipeline_annotations/'
PRIMITIVES_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/mlblocks_primitives/'

@click.argument('pipeline', type=str)
@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
def runCommand(pipeline, datapath):
    """Runs the given pipeline with the given data"""
    pipelinePath = PIPELINE_DIR + pipeline + "_pipeline.json"
    if(not path.exists(pipelinePath)):
        print(f"ERROR: The pipeline you specified '{pipeline}' could not be found in: '{pipelinePath}'")
        return
    # From the data file find the dataset / dataframe (must exist)
    dataDir, dataname = path.split(datapath)
    datasetPath = dataDir + "/data_conf/" + dataname + ".dataset"
    if(not path.exists(datasetPath)):
        print(f"ERROR: The data you specified '{datapath}' does not have an associated dataset. Please create one.")
        return
    
    # print(sys.path)
    # return
    mlblocks.add_primitives_path(PRIMITIVES_PATH)
    mlPipeline = MLPipeline.load(pipelinePath)
    with open(datasetPath, 'rb') as datasetFile:
        dataset : Dataset = pickle.load(datasetFile)
    X_train, _, y_train, _ = dataset.get_splits()
    mlPipeline.fit(X_train, y_train)
    # Save the resulting output (Either a model, or a dataset, or something)