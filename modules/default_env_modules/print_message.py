import click
import pathlib
import sys
from pprint import pprint
import cowsay

@click.option('--message', '-m', type=str, default='Hello!', help='message to print')
def runCommand(message):
    cowsay.cow('Hello World')
    # print(sys.executable)
    # pprint(sys.modules)
    # print(message)
    # print(pathlib.Path(__file__).parent.resolve()) # Change this into a command that is meant to display the directory of modules + assets