from pathlib import Path

def exampleModule():
    parentDir = Path(__file__).parents[1]
    print(parentDir)