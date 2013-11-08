import os
import datetime
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SyncEventHandler(FileSystemEventHandler):
  """Logs all the events captured."""

  def on_moved(self, event):
    super(SyncEventHandler, self).on_moved(event)

    what = 'directory' if event.is_directory else 'file'
    logging.info("Moved %s: from %s to %s", what, event.src_path,
                 event.dest_path)

  def on_created(self, event):
    super(SyncEventHandler, self).on_created(event)

    what = 'directory' if event.is_directory else 'file'
    logging.info("Created %s: %s", what, event.src_path)

  def on_deleted(self, event):
    super(SyncEventHandler, self).on_deleted(event)

    what = 'directory' if event.is_directory else 'file'
    logging.info("Deleted %s: %s", what, event.src_path)

  def on_modified(self, event):
    super(SyncEventHandler, self).on_modified(event)

    what = 'directory' if event.is_directory else 'file'
    logging.info("Modified %s: %s", what, event.src_path)




def modification_date(base_path, filename):
    t = os.path.getmtime(os.path.join(base_path, filename))
    return t
    #return datetime.datetime.fromtimestamp(t)

def modification_dir(base_path):
    timestamps.clear()
    for file in os.listdir(base_path):
        modTime = modification_date(base_path, file)
        timestamps[file] = modTime
    print timestamps

def watchDog(base_path):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = SyncEventHandler()
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

timestamps = dict()
path = sys.argv[1] if len(sys.argv) > 1 else '.'
modification_dir(path)
watchDog(path)