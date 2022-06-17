import click
# import cowsay
import sys

@click.option('--message', '-m', type=str, default='Hello!', help='message to print')
def runCommand(message):
    print(sys.path)
    # cowsay.cow(message)