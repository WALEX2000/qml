import os
import sys

def runEvent(event):
    (_, filename) = os.path.split(event.src_path)
    if(filename.endswith('.tmp')):
        return # Ignore .tmp files

    # print('\nEvent: ' + str(event))
    print('\n Event Exec: ' + sys.executable)