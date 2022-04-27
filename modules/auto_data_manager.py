from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

observer = Observer()

class DataHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("AAAAAAh")
        return super().on_any_event(event)

    def on_created(self, event):
        print(f"hey, {event.src_path} has been created!")
 
    def on_deleted(self, event):
        print(f"what the f**k! Someone deleted {event.src_path}!")
 
    def on_modified(self, event):
        print(f"hey buddy, {event.src_path} has been modified")
 
    def on_moved(self, event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

def watchData(dataFolder):
    print("\n-> Setting up Bakcground Processes..")
    eventHandler = DataHandler()
    observer.schedule(eventHandler, path=dataFolder, recursive=False)
    observer.start()

def stopWatch():
    observer.stop()
    observer.join()