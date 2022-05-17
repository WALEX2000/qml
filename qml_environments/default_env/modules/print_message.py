import click
import pathlib

@click.option('--message', '-m', type=str, default='Hello!', help='message to print')
def runCommand(message):
    print(message)
    print(pathlib.Path(__file__).parent.resolve()) # Change this into a command that is meant to display the directory of modules + assets