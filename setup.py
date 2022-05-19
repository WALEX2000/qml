import os
from setuptools import setup, find_packages

DEPENDENCIES = ['click', 'watchdog', 'pyyaml']

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "qml",
    version = "0.1.0",
    author = "Alexandre Carqueja",
    author_email = "up201705049@up.pt",
    description = ("A framework to manage local Machine Learning pipelines"),
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
    install_requires=DEPENDENCIES,
    py_modules = ['qml', 'modules', 'qml_environments'],
    packages=find_packages(),
    package_data={'qml_environments': ['*']},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'qml=qml:cli'
        ]
    },
    python_requires='~=3.8'
)