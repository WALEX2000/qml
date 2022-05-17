import sys
import click
import pathlib

@click.option('--message', '-m', type=str, default='Hello!', help='message to print')
def runCommand(message):
    print(message)