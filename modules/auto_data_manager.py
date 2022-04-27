import time 
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

observer = Observer()

class DataHandler(FileSystemEventHandler):
    def on_created(event):
        print(f"hey, {event.src_path} has been created!")
 
    def on_deleted(event):
        print(f"what the f**k! Someone deleted {event.src_path}!")
 
    def on_modified(event):
        print(f"hey buddy, {event.src_path} has been modified")
 
    def on_moved(event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

def watchData(dataFolder):
    eventHandler = DataHandler()
    observer.schedule(eventHandler, path=dataFolder, recursive=True, )
    observer.start()

def stopWatch():
    observer.stop()
    observer.join()