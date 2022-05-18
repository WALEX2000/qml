import click
import cowsay

@click.option('--message', '-m', type=str, default='Hello!', help='message to print')
def runCommand(message):
    cowsay.cow(message)