import click
from modules.general_utils import ProjectSettings

PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/pipeline_annotations/'
PRIMITIVES_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/mlblocks_primitives/'
DATA_DIR = ProjectSettings.getProjPath() + '/data/'
DATACONF_DIR = ProjectSettings.getProjPath() + '/data/data_conf/'

@click.argument('pipeline', type=str)
@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
@click.option('--save-data', '-sd', type=str, help='Save the data that is outputted by the fit process, with the specified name.', default = "")
@click.option('--full-data', '-fd', is_flag=True, help='Run the pipeline without spslitting the dataset into train and test sets (should only be used when all the data is being transformed)')
@click.option('--start-index', '-si', type=int, help='The index of the primitive in which to start running the pipeline', default=0)
@click.option('--end-index', '-ei', type=int, help='The index of the primitive in which to stop running the pipeline', default=-1)
@click.option('--save-pipeline', '-sp', is_flag=True, help='Save the pipeline after it has been trained on the given data')
@click.pass_context
def runCommand(ctx, pipeline, datapath, save_data, full_data, start_index, end_index, save_pipeline):
    """Runs the given pipeline with the given data, and, optionally, with the given extra arguments"""
    if(len(ctx.args) % 2 != 0):
        print("ERROR: The Extra arguments you've passed do not comply with the appropriate format.\nPlease use: --arg value")
        return
    extraArgs = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}

    print("...Starting Pipeline Run")
    from mlprimitives.datasets import Dataset
    from mlblocks import add_primitives_path, MLPipeline
    from os import path
    from pickle import load as pickle_load, dump as pickle_dump
    import pandas as pd
    
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
    
    add_primitives_path(PRIMITIVES_PATH)
    mlPipeline : MLPipeline = MLPipeline.load(pipelinePath)
    with open(datasetPath, 'rb') as datasetFile:
        dataset : Dataset = pickle_load(datasetFile)
    
    X_train, X_test, y_train, y_test = dataset.get_splits()
    X_full = pd.concat([X_train, X_test])
    y_full = pd.concat([y_train, y_test])

    if(full_data):
        used_X = X_full
        used_y = y_full
    else:
        used_X = X_train
        used_y = y_train

    if(end_index == -1):
        outputNum = len(mlPipeline.blocks) - 1
    else:
        outputNum = end_index

    print("...Fitting Pipeline")
    context : dict = mlPipeline.fit(used_X, used_y, output_=outputNum, start_=start_index, **extraArgs)
    print("...Fitting Completed Successfuly!")
    if(save_data == ""): return #TODO Save the entire context somewhere?
    
    newDataPath = DATA_DIR + save_data + ".csv"
    print(f"...Saving data to '{newDataPath}'")
    
    X = context.get('X')
    if X is None:
        print("ERROR: Couldn't save data because Pipeline does not output any features as 'X'")
        return
    y = context.get('y')
    if y is None:
        print("ERROR: Couldn't save data because Pipeline does not output any labels as 'y'")
        return
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
    if(full_data):
        if(X.shape[1] == X_train.shape[1] and y.shape[1] == y_train.shape[1]):
            X.columns = list(X_train.columns)
            y.columns = list(y_train.columns)
        fullDataset : pd.DataFrame = X.join(y)
    else:
        if(X.shape[1] != X_test.shape[1] or y.shape[1] != y_test.shape[1]):
            print("ERROR: The pipeline you've run alters the shape of the data, as such if you wish to save the output you must run with the full-data option enabled.")
            return
        X.columns = list(X_train.columns)
        y.columns = list(y_train.columns)
        fullX = pd.merge(X, X_test, how="outer", sort=True)
        fullY = pd.concat([y, y_test], sort=True)
        fullY.sort_index(inplace=True)
        fullDataset : pd.DataFrame = fullX.join(fullY)
    
    dataset.data = fullDataset
    fullDataset.to_csv(newDataPath, index=False)
    newDatasetPath = DATACONF_DIR + save_data + ".csv.dataset"
    with open(newDatasetPath, 'wb') as datasetFile:
        pickle_dump(dataset, datasetFile)