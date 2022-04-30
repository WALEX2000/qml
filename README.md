# QML
## Setup
To install for prod. run: 
    python setup.py sdist bdist_wheel (To build)
    pipx install . --force (To install)
To install for dev. run:
    pipenv shell
    then, just call qml (It's already on the path)

qml is a tool to quickstart machine learning projects, while supporting lightweight MLOps tasks

## Folder Structure
To create a new Pipeline Environment Configuration file, add it to the root of 'qml_assets' directory.
Make sure to make  the property 'name' the same as the file name (without the initial . and the .yaml extension)

Create a sub-directory inside qml_assets with the following name <env-name>-assets.
Here you'll place all assets to be used inside your project

In the modules directory, create a sub-directory with the following name: <env-name>-modules
All modules (commands, event processes, and setup processes), should be placed inside this new folder.
(TODO: This might not be a good idea, as I'll have to duplicate files if i want to re-use them from other pipelines)
