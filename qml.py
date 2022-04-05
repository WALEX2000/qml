import typer
import click
import os

def setupFolderStructure(name):
    mode = 0o777
    # Create Paths
    rootPath = os.path.join(os.getcwd(), name)
    dataPath = os.path.join(rootPath, 'data')
    srcPath = os.path.join(rootPath, 'src')
    mlPrimitivesPath = os.path.join(srcPath, 'ml_primitives')
    pipelinesPath = os.path.join(srcPath, 'pipelines')
    # Create Folders
    os.mkdir(rootPath, mode)
    os.mkdir(dataPath, mode)
    os.mkdir(srcPath, mode)
    os.mkdir(mlPrimitivesPath, mode)
    os.mkdir(pipelinesPath, mode)

@click.command()
@click.option('-n', '--name', type=str, help='Name of root project directory', default='Root_of_Project')
def setup(name):
    print("Commencing Setup...")
    setupFolderStructure(name)
    # -- Add Template Files --
    # -- Initialize git --
    # -- Initialize DVC --


    print("Setup Complete")

@click.command()
def stuff():
    print("Doing a lot of stuff...")


app = typer.Typer()
@app.callback()
def callback():
    """
    Necessary for Typer to work with Clicker
    """

typer_click_object = typer.main.get_command(app)
typer_click_object.add_command(setup, "setup")
typer_click_object.add_command(stuff, "stuff")

@app.command()
def cli():
    typer_click_object()

if __name__ == "__main__":
    typer_click_object()