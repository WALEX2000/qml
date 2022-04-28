from pathlib import Path
import os
import subprocess
import time

def exampleModule():
    os.system('/bin/bash --rcfile /Users/alexandrecarqueja/.local/share/virtualenvs/AAA-QpMT3r5O/bin/activate')
    print(time.ctime())

def ex2():
    python_bin = "/Users/alexandrecarqueja/.local/share/virtualenvs/AAA-QpMT3r5O/bin/python"
    subprocess.Popen([python_bin, ])

def hi():
    print("HIIII")