import click
from modules.general_utils import ProjectSettings

PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/fitted_pipelines/'
PRIMITIVES_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/mlblocks_primitives/'

@click.argument('pipeline', type=str)
@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
def runCommand(pipeline, datapath):
    print("...Starting Pipeline Test")
    from mlprimitives.datasets import Dataset
    from mlblocks import add_primitives_path, MLPipeline
    from os import path
    from pickle import load as pickle_load, dump as pickle_dump
    import pandas as pd
    # Load the trained pipeline
    pipelinePath = PIPELINE_DIR + pipeline + "_fitted.pipeline"
    if(not path.exists(pipelinePath)):
        print(f"ERROR: The pipeline you specified '{pipeline}' is not fitted. It could not be found in: '{pipelinePath}'")
        return
    # From the data file find the dataset / dataframe (must exist)
    dataDir, dataname = path.split(datapath)
    datasetPath = dataDir + "/data_conf/" + dataname + ".dataset"
    if(not path.exists(datasetPath)):
        print(f"ERROR: The data you specified '{datapath}' does not have an associated dataset. Please create one.")
        return

    add_primitives_path(PRIMITIVES_PATH)
    with open(pipelinePath, 'rb') as pipelineFile:
        mlPipeline : MLPipeline = pickle_load(pipelineFile)
    with open(datasetPath, 'rb') as datasetFile:
        dataset : Dataset = pickle_load(datasetFile)
    
    _, X_test, _, y_test = dataset.get_splits()
    predictions = mlPipeline.predict(X_test)
    score = dataset.score(y_test, predictions)
    print('Test Score: ' + score)