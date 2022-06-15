import click
from modules.general_utils import ProjectSettings, getAssetPath, CLIexec

PIPELINE_DIR = ProjectSettings.getProjPath() + '/src/ml_pipelines/fitted_pipelines/'

@click.argument('pipeline', type=str)
@click.option('--image-name', '-i', type=str, help='Set a custom name for the docker image. Defaults to <pipeline>_image.', default="")
def runCommand(pipeline, image_name):
    from os import path
    import tempfile
    from distutils.dir_util import copy_tree
    from pathlib import Path
    from shutil import copyfile
    
    pipelinePath = PIPELINE_DIR + pipeline + "_fitted.pipeline"
    if(not path.exists(pipelinePath)):
        print(f"ERROR: The pipeline you specified '{pipeline}' is not fitted. It could not be found in: '{pipelinePath}'")
        return
    
    if(image_name == ""): image_name = pipeline + "_image"
    image_name = str.lower(image_name)
    with tempfile.TemporaryDirectory() as tmpdirname:
        dirPath = getAssetPath('deployables')
        copy_tree(dirPath, tmpdirname)
        copyfile(pipelinePath, tmpdirname+'/app/model.pipeline')
        requirementsPath = ProjectSettings.getProjPath() + '/requirements.txt'
        copyfile(requirementsPath, tmpdirname+'/proj_requirements.txt')
        
        cmd = f"docker build -t {image_name} {tmpdirname}"
        print('Building Docker Image..')
        if(not CLIexec(cmd)):
            print('ERROR: Could not run docker to build the image. Please make sure docker is installed and running.')

    print(f'Docker Image was successfully created under the name {image_name}')
    