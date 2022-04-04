from importlib.metadata import requires
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "qml",
    version = "0.0.1",
    author = "Alexandre Carqueja",
    author_email = "up201705049@up.pt",
    description = ("A framework to manage quick Machine Learning projects"),
    license = "MIT",
    keywords = "machine learning devops mlops",
    #url = "",
    long_description=read('README.md'),
    long_description_content_type = "text/markdown",
    classifiers=[
        "Development Status ::  Pre-Alpha",
        "Topic :: MLOps",
        "License :: OSI Approved :: BSD License",
    ],
    requires=read('Pipfile'),
    py_modules = ['cliInterface.py', 'src'],
    packages=find_packages(),
    entry_points = '''
        [console_scripts]
        qml=cliInterface:cli
    ''',
    python_requires='>=3.7'
)