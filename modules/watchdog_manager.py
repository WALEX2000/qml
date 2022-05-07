from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from modules.general_utils import ProjectSettings, runEvents

observer = Observer()

class DirDog(FileSystemEventHandler):
    def __init__(self, eventsDict : dict):
        self.anyActions : list[str] = eventsDict.get('on_any_event')
        self.createActions : list[str] = eventsDict.get('on_create')
        self.deleteActions : list[str] = eventsDict.get('on_deleted')
        self.modifyActions : list[str] = eventsDict.get('on_modified')
        self.moveActions : list[str] = eventsDict.get('on_moved')

    def on_any_event(self, event):
        if self.anyActions is not None:
            runEvents(self.anyActions, event)

    def on_created(self, event):
        if self.createActions is not None:
            runEvents(self.createActions, event)
 
    def on_deleted(self, event):
        if self.deleteActions is not None:
            runEvents(self.deleteActions, event)
 
    def on_modified(self, event):
        if self.modifyActions is not None:
            runEvents(self.modifyActions, event)
 
    def on_moved(self, event):
        if self.moveActions is not None:
            runEvents(self.moveActions, event)

def launchWatchDogs(dirList : list[dict]):
    projPath = ProjectSettings.getProjPath()
    for dir in dirList:
        dirName = dir.get('directory')
        if(dirName is None):
            print('ENV WARNING: A watchdog entry was found with no specified directory:\n' + dir + '\n')
            continue
        directory = projPath + '/' + dirName
        events : dict = dir.get('events')
        if(events is None):
            print('ENV WARNING: The specified watchdog directory: ' + dirName + ' does not contain any specified events')
            continue
        eventHandler = DirDog(events)
        observer.schedule(eventHandler, path=directory, recursive=False)
    observer.start()

def stopWatchDogs():
    observer.stop()
    observer.join()