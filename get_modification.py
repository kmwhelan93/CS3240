import os
import datetime
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SyncEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, q, path):
        self.timestamps = dict()
        #path = sys.argv[1] if len(sys.argv) > 1 else '.'
        self.modification_dir(path)
        self.q = q

    def on_moved(self, event):
        super(SyncEventHandler, self).on_moved(event)
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Moved %s: from %s to %s", what, event.src_path,
        #             event.dest_path)
        if (self.valid_path(event.src_path) and self.valid_path(event.dest_path)):
            object = {"command":"move", "file": {"src": event.src_path, "dest": event.dest_path }}
            self.q.put(object)

    def on_created(self, event):
        super(SyncEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Created %s: %s", what, event.src_path)
        self.create_object("create", event.src_path)

    def on_deleted(self, event):
        super(SyncEventHandler, self).on_deleted(event)
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Deleted %s: %s", what, event.src_path)
        self.create_object("delete", event.src_path)


    def on_modified(self, event):
        super(SyncEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Modified %s: %s", what, event.src_path)
        self.create_object("put", event.src_path)

    def modification_date(self, base_path, filename):
        t = os.path.getmtime(os.path.join(base_path, filename))
        return t
        #return datetime.datetime.fromtimestamp(t)

    def modification_dir(self, base_path):
        self.timestamps.clear()
        for file in os.listdir(base_path):
            modTime = self.modification_date(base_path, file)
            self.timestamps[file] = modTime
            #print self.timestamps

    def create_object(self, command, path):
        if (self.valid_path(path)):
            o = {"command" : command, "file" : path}
            self.q.put(o)
        #o = {"command": "put", "files": self.timestamps.items()}

    def valid_path(self, path):
        if path.find(".goutputstream") != -1:
            return False
        if path.endswith("~"):
            return False
        return True