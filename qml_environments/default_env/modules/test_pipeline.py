import click
from modules.general_utils import ProjectSettings
from qml_environments.default_env.modules.inspect_data import saveMetadata, getMetadata

PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/fitted_pipelines/'
PRIMITIVES_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/mlblocks_primitives/'

@click.argument('pipeline', type=str)
@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
def runCommand(pipeline, datapath):
    print("...Starting Pipeline Test")
    from qml_custom.data_handler import DataHandler
    from mlblocks import add_primitives_path, MLPipeline
    from os import path
    from pickle import load as pickle_load
    
    pipelinePath = PIPELINE_DIR + pipeline + "_fitted.pipeline"
    if(not path.exists(pipelinePath)):
        print(f"ERROR: The pipeline you specified '{pipeline}' is not fitted. It could not be found in: '{pipelinePath}'")
        return
    
    handler : DataHandler = DataHandler.load(datapath)
    if(handler is None):
        print(f"ERROR: The data you specified '{datapath}' does not have an associated handler. Please create one.")
        return

    add_primitives_path(PRIMITIVES_PATH)
    with open(pipelinePath, 'rb') as pipelineFile:
        mlPipeline : MLPipeline = pickle_load(pipelineFile)
    
    _, X_test, _, y_test = handler.getSplit()
    predictions = mlPipeline.predict(X_test)
    score = handler.score(y_test, predictions)
    print('Test Score:\n' + str(score))

    dvcPath = pipelinePath + '.dvc'
    metaInfo = getMetadata(dvcPath)
    if(metaInfo is None): return

    metaInfo['score'] = str(score)
    saveMetadata(dvcPath, metaInfo)