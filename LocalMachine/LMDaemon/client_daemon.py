from threading import Thread
from socket import socket
from Queue import Queue
#from command_thread import command_thread
import thread
import time
import logging

import json

from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, stdio, defer

from twisted.internet import task

from get_modification import SyncEventHandler
from watchdog.observers import Observer
from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input

import os
import shutil
import optparse


class Echo(LineReceiver):
    delimiter = '\n'

    def __init__(self, q, files_path='/home/student/Documents/CSA/local/', server_ip='127.0.0.1', server_port=1234):
        self.q = q
        self.server_ip = server_ip
        self.server_port = server_port
        self.files_path = files_path
        self.connected = False
        self.ignore = []

        self.file_handler = None
        self.file_data = ()

    def connectionMade(self):

        self.connected = False
        self.task_id = task.LoopingCall(self.callback)
        self.task_id.start(.5)
        #self.setLineMode()
        task.LoopingCall(self.get_files).start(10)

    def get_files(self):
        username = "kevin"
        password = "kevin"
        timestamps = self.get_timestamps()
        object = {"command": "get", "username": username, "password": password, "timestamps": timestamps}
        self.q.put(object)

    def callback(self):
        #print 'callback'
        if (self.connected == True and self.q.qsize() > 0):
            next_command = self.q.get()
            self._sendCommand(next_command)
            #self._sendCommand(next_command)

    def dataReceived(self, data):
        if (data == "init\n"):
            self.connected = True
        else:
            files = json.loads(data.strip())
            # get directories first
            files['directories'].sort()
            directories = []
            for file in files['remove']:
                path = os.path.join(self.files_path, file)
                if os.path.isfile(path):
                    os.unlink(path)
                else:
                    directories.append(path)
            directories.sort(reverse=True)
            for dir in directories:
                if os.path.isdir(dir):
                    shutil.rmtree(dir)

            for directory in files['directories']:
                path = os.path.join(self.files_path, directory)
                if not os.path.exists(path):
                    os.mkdir(path)
                self.ignore.append(path)
            # because files need the directories to exist
            for file, content in files['files'].iteritems():
                path = os.path.join(self.files_path, file)
                f = open(path, 'w')
                f.write(content['content'] +'')
                f.close()
                self.ignore.append(path)

    def _sendCommand(self, object):
        object["username"] = "kevin"
        object["password"] = "kevin"
        sendObj = {"username": "kevin", "password": "kevin"}
        command = object["command"]
        if command == 'move' or command=='create' or command=='get':
            if command=='create' and object['file'] in self.ignore:
                self.ignore.remove(object['file'])
                return
            self.sendLine(json.dumps(object))
        elif command == 'put':
            if object['file'] in self.ignore:
                self.ignore.remove(object['file'])
                return
            try:
                file_path = object['file']
                filename = object['file'].replace(self.files_path, "")
            except IndexError:
                self._display_message('Missing local file path or remote file name')
                return

            if not os.path.isfile(file_path):
                self._display_message('This file does not exist')
                return

            file_size = os.path.getsize(file_path) / 1024

            print 'Uploading file: %s (%d KB)' % (filename, file_size)
            f = open(file_path, 'r')
            object = {"command": "put", "local": filename, "content": f.read()}
            sendObj = dict(object.items() + sendObj.items())
            self.sendLine(json.dumps(sendObj))
            f.close()
    def _display_message(self, message):
        print message


    def modification_date(self, filename):
        t = os.path.getmtime(os.path.join(self.files_path, filename))
        return t
        #return datetime.datetime.fromtimestamp(t)

    def get_timestamps(self):
        timestamps = {}
        for file in os.listdir(self.files_path):
            modTime = self.modification_date(file)
            timestamps[file] = modTime
            #print self.timestamps
        return timestamps


class EchoClientFactory(ClientFactory):
    def __init__(self, q, files_path):
        self.q = q
        self.files_path = files_path

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.echo = Echo(self.q, self.files_path)
        return self.echo

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

files_path = '/home/student/Documents/CSA/local/'

def watchDog(base_path, q):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = SyncEventHandler(q, base_path)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


q = Queue()

thread.start_new_thread(watchDog, (files_path, q, ))


factory = EchoClientFactory(q, files_path)
reactor.connectTCP("localhost", 1234, factory)
reactor.run()








