import click
from modules.general_utils import ProjectSettings, CLIexecSync
from qml_environments.default_env.modules.inspect_data import saveMetadata, hashFile

PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/pipeline_annotations/'
FITTED_PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/fitted_pipelines/'
PRIMITIVES_PATH = ProjectSettings.getProjPath() + '/src/ml_pipelines/mlblocks_primitives/'
DATA_DIR = ProjectSettings.getProjPath() + '/data/'
DATACONF_DIR = ProjectSettings.getProjPath() + '/data/data_conf/'

def autoTune(mlPipeline, extraArgs, start_index, outputNum, handler):
    from btb.tuning import Tunable
    from btb import BTBSession
    import pandas as pd
    from qml_custom.data_handler import DataHandler
    from mlblocks import MLPipeline

    hyperParamsDict = mlPipeline.get_tunable_hyperparameters()
    tunablesDict = {}
    X, _, y, _ = handler.getSplit()
    fullDataset : pd.DataFrame = X.join(y)
    train = fullDataset.sample(frac=0.8, random_state=25)
    val = fullDataset.drop(train.index)
    X_train = train.drop(columns=y.name)
    X_val = val.drop(columns=y.name)
    y_train = train.loc[:,y.name]
    y_val = val.loc[:,y.name]

    for block in hyperParamsDict:
        dictionary = hyperParamsDict[block]
        tunable : Tunable = Tunable.from_dict(dictionary)
        tunablesDict[block] = tunable
    
    def runPipeline(blockName, hyperParams):
        hyperDict = {blockName : hyperParams}
        mlPipeline.set_hyperparameters(hyperDict)
        try:
            mlPipeline.fit(X_train, y_train, output_=outputNum, start_=start_index, **extraArgs)
            pred = mlPipeline.predict(X_val)
            score = handler.score(y_val, pred)
        except:
            score = 0
        return score
    
    session = BTBSession(tunables=tunablesDict,scorer=runPipeline, verbose=True)
    best_proposal = session.run(100)
    print('Validation Score: ' + str(best_proposal['score']))
    return best_proposal

@click.argument('pipeline', type=str)
@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
@click.option('--save-data', '-sd', type=str, help='Save the data that is outputted by the fit process, with the specified name.', default = "")
@click.option('--full-data', '-fd', is_flag=True, help='Run the pipeline without spslitting the data into train and test sets (should only be used when all the data is being transformed)')
@click.option('--start-index', '-si', type=int, help='The index of the primitive in which to start running the pipeline', default=0)
@click.option('--end-index', '-ei', type=int, help='The index of the primitive in which to stop running the pipeline', default=-1)
@click.option('--save-pipeline', '-sp', is_flag=True, help='Save the pipeline after it has been trained on the given data')
@click.option('--auto-tune', '-at', is_flag=True, help='Optimize the ML Networks Hyperparameters automatically')
@click.pass_context
def runCommand(ctx, pipeline, datapath, save_data, full_data, start_index, end_index, save_pipeline, auto_tune):
    """Runs the given pipeline with the given data, and, optionally, with the given extra arguments"""
    if(len(ctx.args) % 2 != 0):
        print("ERROR: The Extra arguments you've passed do not comply with the appropriate format.\nPlease use: --arg value")
        return
    extraArgs = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}

    print("...Starting Pipeline Run")
    from mlblocks import add_primitives_path, MLPipeline
    from os import path
    from pickle import dump as pickle_dump
    import pandas as pd
    
    pipelinePath = PIPELINE_DIR + pipeline + "_pipeline.json"
    if(not path.exists(pipelinePath)):
        print(f"ERROR: The pipeline you specified '{pipeline}' could not be found in: '{pipelinePath}'")
        return
    
    add_primitives_path(PRIMITIVES_PATH)
    mlPipeline : MLPipeline = MLPipeline.load(pipelinePath)
    handler : DataHandler = DataHandler.load(datapath)
    if(handler is None):
        print(f"ERROR: The data you specified '{datapath}' does not have an associated handler. Please create one.")
        return
    
    X_train, X_test, y_train, y_test = handler.getSplit()
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
    
    if(auto_tune):
        print("...Starting Pipeline Auto-Tune")
        best_proposal = autoTune(mlPipeline, extraArgs, start_index, outputNum, handler)
        newHyperParameters = {best_proposal['name'] : best_proposal['config']}
        mlPipeline.set_hyperparameters(newHyperParameters)
        print("...Pipeline Auto-Tune Complete!")
    
    print("...Fitting Pipeline")
    context : dict = mlPipeline.fit(used_X, used_y, output_=outputNum, start_=start_index, **extraArgs)
    print("...Fitting Completed Successfuly!")

    if(save_pipeline):
        print("...Saving Pipeline")
        pipelinePath = FITTED_PIPELINE_DIR + pipeline + "_fitted.pipeline"
        with open(pipelinePath, 'wb') as pipelineFile:
            pickle_dump(mlPipeline, pipelineFile)
        
        dvcPath = pipelinePath + ".dvc"
        if(not path.exists(dvcPath)):
            print("...Adding Pipeline to DVC")
            command = 'dvc add ' + pipelinePath
            CLIexecSync(command, ProjectSettings.getProjPath(), display=False)
        
        _, dataName = path.split(datapath)
        hashValue = hashFile(datapath)
        trainedWith = dataName + '#' + hashValue
        metaInfo = {
            'trained_with':trainedWith,
            'score':'None'
        }
        saveMetadata(dvcPath, metaInfo)
        print("...Pipeline Save Complete!")

    if(save_data == ""): return
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
        if isinstance(y_train, pd.Series):
            y_train = pd.DataFrame(y_train)
        if(X.shape[1] == X_train.shape[1] and y.shape[1] == y_train.shape[1]):
            X.columns = list(X_train.columns)
            y.columns = list(y_train.columns)
        fullDataset : pd.DataFrame = X.join(y)
    else:
        if isinstance(y, pd.Series):
            y = pd.DataFrame(y)
        if isinstance(y_test, pd.Series):
            y_test = pd.DataFrame(y_test)
            
        if(X.shape[1] != X_test.shape[1] or y.shape[1] != y_test.shape[1]):
            print("ERROR: The pipeline you've run alters the shape of the data, as such if you wish to save the output you must run with the full-data option enabled.")
            return
        X.columns = list(X_train.columns)
        y.columns = list(y_train.columns)
        fullX = pd.merge(X, X_test, how="outer", sort=True)
        fullY = pd.concat([y, y_test], sort=True)
        fullY.sort_index(inplace=True)
        fullDataset : pd.DataFrame = fullX.join(fullY)
    
    fullDataset.to_csv(newDataPath, index=False)
    newHandlerPath = DATACONF_DIR + save_data + ".csv.handler"
    handler.save(newHandlerPath)
