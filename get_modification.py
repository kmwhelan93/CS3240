import os
import datetime
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SyncEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, q, path, ignore, f):
        self.timestamps = dict()
        self.base_path = path
        self.q = q
        self.ignore = ignore
        self.f = f
        print self.f.file_syncing

    def on_moved(self, event):
        super(SyncEventHandler, self).on_moved(event)
        print "moved"
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Moved %s: from %s to %s", what, event.src_path,
        #             event.dest_path)
        if (self.valid_path(event.src_path) and self.valid_path(event.dest_path)):
            self.ignore.append(self.clean_file_string(self.get_local_path(event.src_path)))
            object = {"command":"move", "src": self.get_local_path(event.src_path), "dest": self.get_local_path(event.dest_path) }
            self.q.append(object)

    def on_created(self, event):
        super(SyncEventHandler, self).on_created(event)
        print "created"
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Created %s: %s", what, event.src_path)
        if (self.valid_path(event.src_path) and what=='directory'):
            object = {"command": "create", "file": self.get_local_path(event.src_path), "what": what}
            self.q.append(object)

    def on_deleted(self, event):
        super(SyncEventHandler, self).on_deleted(event)
        time.sleep(1)
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Deleted %s: %s", what, event.src_path)
        if self.valid_path(event.src_path):
            object = {"command": "delete", "file": self.get_local_path(event.src_path), "what": what}
            self.q.append(object)

    def on_modified(self, event):
        super(SyncEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        #logging.info("Modified %s: %s", what, event.src_path)
        if self.valid_path(event.src_path):
            self.create_object("put", event.src_path)

    def create_object(self, command, path):
        if (self.valid_path(path)):
            o = {"command" : command, "file" : path}
            self.q.append(o)
        #o = {"command": "put", "files": self.timestamps.items()}

    def valid_path(self, path):
        if path == None:
            return False
        if path.find(".goutputstream") != -1:
            return False
        if path == self.f.file_syncing:
            return False
        return True

    def clean_file_string(self, string):
        if (len(string) > 0):
            if string[0] == '/':
                return string[1:]
        return string

    def get_local_path(self, full_path):
        return full_path.replace(self.base_path, '')