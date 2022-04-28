from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileCreatedEvent
from watchdog.events import FileMovedEvent
from watchdog.events import FileDeletedEvent
from watchdog.events import FileModifiedEvent
from watchdog.events import FileMovedEvent
from . import cli_utils
from . import data_inspector
import os
import time

observer = Observer()

class DataHandler(FileSystemEventHandler):
    def __init__(self, dataPath, rootPath):
        self.dataPath = dataPath
        self.rootPath = rootPath

    def on_any_event(self, event):
        pass

    def on_created(self, event):
        if(isinstance(event, FileCreatedEvent)):
            print("\n" + event._src_path + " was Created!")
            if(event.is_synthetic):
                print(event.src_path + " generated a Synth Event")
            # Add file to DVC
            (_, filename) = os.path.split(event.src_path.lower()) # Head is path info, tail is name info
            if(filename.endswith('.tmp')):
                return
            command = 'dvc add ' + event.src_path + ' --file ' + self.dataPath + '/dataConf/' + filename + '.dvc --no-commit'
            cli_utils.CLIexec(command, self.rootPath)
            # Create profile for dataFile
            data_inspector.inspectData(event.src_path)

 
    def on_deleted(self, event):
        if(isinstance(event, FileDeletedEvent)):
            print("\n" + event.src_path + " was deleted!")
            if(event.is_synthetic):
                print(event.src_path + " generated a Synth Event")
        # not sure if I should automatically undo dvc / profile or not
 
    def on_modified(self, event):
        if(isinstance(event, FileModifiedEvent)):
            print("\n" + event.src_path + " was modified!")
            if(event.is_synthetic):
                print(event.src_path + " generated a Synth Event")
        # For now I don't think there's anything that I should do here (But this could be automated as well)
 
    def on_moved(self, event):
        if(isinstance(event, FileMovedEvent)):
            print("\n" + event._src_path + " was moved to:\n" + event.dest_path)
            if(event.is_synthetic):
                print(event.src_path + " generated a Synth Event")
        # if moved into data
        # add dataset to dvc
        # create profile for dataFile

def watchData(dataPath, rootPath):
    eventHandler = DataHandler(dataPath, rootPath)
    observer.schedule(eventHandler, path=dataPath, recursive=False)
    observer.start()

def stopWatch():
    observer.stop()
    observer.join()