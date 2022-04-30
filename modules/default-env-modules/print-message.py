import click

@click.option('--message', '-m', type=str, default='Hello!', help='message to print')
def runCommand(message):
    print(message)