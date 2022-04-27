import typer
import click
from modules import example_module
from modules import data_inspector
from modules import project_initializer

@click.command()
@click.option('-n', '--name', type=str, help='Name of root project directory', default='Root_of_Project')
def init(name):
    project_initializer.setupProject(name)

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--checkpoint', '-ch', is_flag=True, help='Generate a Great Expectations checkpoint for this dataset')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def inspect_data(filename, checkpoint, args):
    parsedArgs = ' ' + ' '.join(args)
    data_inspector.inspectData(filename, parsedArgs)

@click.command()
def stuff():
    example_module.exampleModule()


app = typer.Typer()
@app.callback()
def callback():
    """
    Necessary for Typer to work with Clicker
    """

typer_click_object = typer.main.get_command(app)
typer_click_object.add_command(init, "init")
typer_click_object.add_command(stuff, "stuff")
typer_click_object.add_command(inspect_data, "inspect-data")

@app.command()
def cli():
    typer_click_object()

if __name__ == "__main__":
    typer_click_object()