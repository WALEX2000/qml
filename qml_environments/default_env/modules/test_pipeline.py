import click

@click.argument('pipeline', type=str)
@click.argument('datapath', type=click.Path(exists=True, dir_okay=False))
def runCommand(pipeline, datapath):
    # Load the trained pipeline
    # Load the dataset
    # Run the pipeline with the dataset
    # Print the score
    pass