import typer
app = typer.Typer()

@app.group()
def cli():
    pass

@app.command()
def setup():
    print("Commencing Setup...")
    # Create folder structure
    # Initialize git
    # Initialize DVC

@app.command()
def stuff():
    print("Doing Stuff...")
    # Create folder structure
    # Initialize git
    # Initialize DVC


if __name__ == '__main__':
    app()